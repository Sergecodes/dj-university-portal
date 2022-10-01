from django import forms
from django.contrib.auth.forms import (
	UserChangeForm as BaseUserChangeForm,
	UserCreationForm as BaseUserCreationForm,
	# ReadOnlyPasswordHashField
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.translation import gettext_lazy as _

from core.constants import CHECK_WHATSAPP, USERNAME_CHANGE_WAIT_PERIOD
from .models import PhoneNumber, User


### Following forms will be used in the admin site.  ###
class AdminUserCreationForm(BaseUserCreationForm):
	class Meta:
		model 	= User
		fields 	= '__all__'


class AdminUserChangeForm(BaseUserChangeForm):
	class Meta:
		model 	= User
		fields 	= '__all__'


### Following forms will be used in the main site.  ###
class UserCreationForm(BaseUserCreationForm):
	# set password2 to None to override parent class field
	password2 = None
	
	class Meta:
		model = User
		fields = [
			'username', 'email', 'password1', 'country', 'first_language', 'gender', 
		]
		# localized_fields = ('birth_date', )
		widgets = {
			# use radio boxes instead of the default select menu
			'first_language': forms.RadioSelect(),
			'gender': forms.RadioSelect(),
		}
		labels = {
			'email': _('Email address')
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# remove autofocus set by superclass on `username_field` (email)
		self.fields['email'].widget.attrs.pop('autofocus')
		self.fields['country'].empty_label = None

		# set class on password field
		# this can't be done on the Meta.widgets object because
		# this field was set in the class definition(super class)
		self.fields['password1'].widget.attrs.update({'class': 'js-password1'})

	def clean(self):
		cleaned_data = super().clean()
		password = cleaned_data.get('password1')

		if password:
			validate_password(password)
		
	def save(self, commit=True):
		# save this object's m2m method..
		# a comment in this method (super().save()) says 
			# If not committing, add a method to the form to allow deferred saving of m2m data.
		if commit == False:
			super().save(commit)

		# *copy* self.cleaned_data 
		data = dict(**self.cleaned_data)
		
		user = User.objects.create_user(
			password=data.pop('password1'), 
			commit=commit, 
			**data
		)
		return user
	
	
class UserUpdateForm(forms.ModelForm):
	"""A form for updating users. Includes all the fields on
	the user, but replaces the password field with admin's
	password hash display field.
	"""
	pass
	# not useful since password field won't be displayed in the form.
	# password = ReadOnlyPasswordHashField()
	
	# set email field as disabled so it won't be submitted and will be uninteractabe
	# & readonly so user won't be able to edit it, but can copy it and click on it
	# this also sets some desired styles from Bootstrap
	# email = forms.EmailField(
	# 	label=_('Email address'),
	# 	# disabled means browser should not send any form data for this field
	# 	widget=forms.EmailInput(attrs={'disabled': '', 'readonly': ''}),
	# 	help_text=_("Email can't be changed"),
	# 	# since disabled is set, browser won't send any form data back for this field
	# 	# so set required to False
	# 	required=False   # see https://stackoverflow.com/a/1424453/
	# )

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['country'].empty_label = None

	class Meta:
		model = User
		fields = ['email', 'username', 'country', 'first_language', 'gender', ]
		widgets = {
			'first_language': forms.RadioSelect(),
			'gender': forms.RadioSelect(),
		}
		help_texts = {
			'email': _("Enter a valid and correct email address, we won't send a verification code")
		}

	def clean_username(self):
		instance, cleaned_data = self.instance, self.cleaned_data

		# If username was changed
		if instance.username != cleaned_data['username']:
			if not instance.can_change_username:
				self.add_error(
					'username', 
					_('You last changed your username on {}. You need to wait until after {} days to be able to change it again.') \
					.format(instance.last_changed_username_datetime.strftime('%d %b %Y, %H:%M'), USERNAME_CHANGE_WAIT_PERIOD.days)
				)
			
		# Note that if error is added to field, it will be removed from cleaned_data
		return cleaned_data.get('username', instance.username)


class PhoneNumberForm(forms.ModelForm):
	class Meta:
		model = PhoneNumber
		fields = ('number', 'can_whatsapp')
		widgets = {
			'number': forms.NumberInput(attrs={'type': 'tel', 'class': 'js-number'}),
		}


# inherit from base class so as to override the clean method of the formset
# class BasePhoneNumberFormset(BaseGenericInlineFormSet):
class BasePhoneNumberFormset(BaseInlineFormSet):
	def clean(self):
		"""
		Checks that no two numbers are the same and that there should be 
		at least one number that supports Whatsapp. 
		Each number should be valid(convertible to int)
		"""
		# first call super method 
		super().clean()
		
		if any(self.errors):
			# don't bother validating the formset if there are already errors in any of its forms
			return

		# at least one form should be present
		if len(self.forms) == 0:
			if CHECK_WHATSAPP:
				msg = _("Enter at least one phone number and this number should support WhatsApp")
			else:
				msg = _("Enter at least one phone number")

			raise ValidationError(msg)

		numbers_list, can_whatsapp_list = [], []
		for form in self.forms:
			if self.can_delete and self._should_delete_form(form):
				continue

			number = form.cleaned_data['number']
			if number in numbers_list:
				raise ValidationError(_("Phone numbers should be unique."))
			
			# remove any space in number and add number to list
			number = number.replace(' ', '')
			numbers_list.append(number)

			if CHECK_WHATSAPP:
				can_whatsapp_list.append(form.cleaned_data['can_whatsapp'])

		# if number is invalid(if number is not int)
		for number in numbers_list:
			try:
				int(number)
			except ValueError:
				raise ValidationError(_("There is an invalid number in the list."))

		# if there isn't any number that supports whatsapp, raise error 
		# also perform this check in frontend
		if CHECK_WHATSAPP:
			if not any(can_whatsapp_list):
				raise ValidationError(_("Enter at least one number that supports WhatsApp."))


PhoneNumberFormset = inlineformset_factory(
	User,
	PhoneNumber, 
	form=PhoneNumberForm, 
	formset=BasePhoneNumberFormset, 
	extra=1   
)

EditPhoneNumberFormset = inlineformset_factory(
	User,
	PhoneNumber, 
	form=PhoneNumberForm, 
	formset=BasePhoneNumberFormset, 
	extra=0   
)
