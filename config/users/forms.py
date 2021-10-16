from django import forms
from django.contrib.auth.forms import (
	UserChangeForm as BaseUserChangeForm,
	UserCreationForm as BaseUserCreationForm,
	# ReadOnlyPasswordHashField
)
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.translation import gettext_lazy as _

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
	
	class Meta:
		model = User
		fields = [
			'full_name', 'username', 'email', 'password1', 
			'password2', 'first_language', 'gender', 
		]
		# localized_fields = ('birth_date', )
		widgets = {
			'full_name': forms.TextInput(attrs={'placeholder': 'Ex. Paul Biya'}),
			'first_language': forms.RadioSelect,
			'gender': forms.RadioSelect,
			# remove default autofocus set by super class
			'email': forms.EmailInput(attrs={'autofocus': 'false'})
		}
		labels = {
			'email': _('Email address')
		}
		help_texts = {
			'email': _("You won't be able to change your email.")
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# remove autofocus set by superclass on `username_field` (email)
		self.fields['email'].widget.attrs.pop('autofocus')

	def save(self, commit=True):
		# save this object's m2m method..
		# a comment in this method (super().save()) says 
			# If not committing, add a method to the form to allow deferred saving of m2m data.
		if commit == False:
			super().save(commit)

		# *copy* self.cleaned_data into a new dict and 
		# remove 'password2' (confirm password) since it's not a field of the User model
		data = dict(**self.cleaned_data)
		data.pop('password2')
		# print(data)
		
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
	# not useful since password field won't be displayed in the form.
	# password = ReadOnlyPasswordHashField()
	
	# set email field as disabled & readonly so user won't be able to interact with it
	# this also sets some desired styles from Bootstrap

	# setting readonly on a widget only makes the input in the browser read-only.  
	# do this "https://stackoverflow.com/a/331550"  (add the disabled attribute to it)
	# to ensure its value doesn't change on form level.  
	# P.S. I can also do this by passing the user object to the form 
	# and setting the initial attribute of the field to the user's email.
	email = forms.EmailField(
		label=_('Email address'),
		# disabled means browser should not send any form data for this field
		widget=forms.EmailInput(attrs={'readonly': '', 'disabled': '',}),
		help_text=_("Email can't be changed"),
		# since disabled is set, browser won't send any form data back for this field
		# so set required to False
		required=False   # see https://stackoverflow.com/a/1424453/
	)

	class Meta:
		model = User
		fields = ['email', 'full_name', 'username', 'first_language', 'gender', ]
		widgets = {
			'first_language': forms.RadioSelect,
			'gender': forms.RadioSelect,
		}

	def clean_email(self):
		# since this field is set to disabled, django ignores its value when the form is submitted.
		# thus if the form had errors, the field is redisplayed with no value.
		# the following permits to reinsert the value in the form

		# instance refers to the User object that submitted the form
		instance = self.instance
		if instance and instance.pk:
			return instance.email


class PhoneNumberForm(forms.ModelForm):
	class Meta:
		model = PhoneNumber
		fields = ('operator', 'number', 'can_whatsapp')
		widgets = {
			'number': forms.NumberInput(attrs={'type': 'tel'}),
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

		# at least one form should be present (since if formset has errors, we won't arrive here)
		assert len(self.forms) >= 1, "At least one form must be present, got none"

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
			can_whatsapp_list.append(form.cleaned_data['can_whatsapp'])

		# if number is invalid(if number is not int)
		for number in numbers_list:
			try:
				int(number)
			except ValueError:
				raise ValidationError(_("There is an invalid number in the list."))

		# if there isn't any number that supports whatsapp, raise error 
		# also perform this check in frontend
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
