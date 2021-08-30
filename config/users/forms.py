from django import forms
from django.contrib.auth.forms import (
	UserChangeForm as BaseUserChangeForm,
	UserCreationForm as BaseUserCreationForm,
	# ReadOnlyPasswordHashField
)
from django.contrib.auth.password_validation import validate_password

# from django.contrib.contenttypes.forms import (
# 	BaseGenericInlineFormSet,
# 	generic_inlineformset_factory
# )
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.translation import ugettext_lazy as _

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
class UserCreationForm(forms.ModelForm):
	"""Form used to register a new user to the site. Includes all the required
    fields, plus a repeated password."""
	password = forms.CharField(
		widget=forms.PasswordInput(),
		required=True
	)
	confirm_password = forms.CharField(
		label=_('Password confirmation'),
		widget=forms.PasswordInput(),
		help_text=_('Enter the same password, for confirmation.'),
		required=True
	)

	def clean_password(self):
		password = self.cleaned_data['password']
		return password

	def clean_confirm_password(self):
		password1 = self.cleaned_data.get('password')
		password2 = self.cleaned_data.get('confirm_password')

		if password1 and password2 and password1 != password2:
			# add error instead of raising error so as to continuer to validation of other fields
			self.add_error('confirm_password', _('The passwords did not match.'))
		else:
			# if both passwords match, validate the password
			validate_password(password2)
			return password2
	
	def save(self, commit=True):
		# save this object's m2m method..
		# a comment in this method (super().save()) says 
			# If not committing, add a method to the form to allow deferred saving of m2m data.
		super().save(commit=False)

		# *copy* self.cleaned_data into a new dict and remove 'confirm_password' since it's not a field of the User model
		data = dict(**self.cleaned_data)
		data.pop('confirm_password', None)
		
		user = User.objects.create_user(commit=commit, **data)
		return user

	
	class Meta:
		model = User
		fields = ['full_name', 'username', 'email', 'password', 'confirm_password', 'first_language', 'gender', ]
		# localized_fields = ('birth_date', )
		widgets = {
			'first_language': forms.RadioSelect,
			'gender': forms.RadioSelect,
			# 'birth_date': forms.DateInput(attrs={'type':'date'})
		}
		labels = {
			'email': _('Email address')
		}
		
	
class UserUpdateForm(forms.ModelForm):
	"""A form for updating users. Includes all the fields on
	the user, but replaces the password field with admin's
	password hash display field.
	"""
	# not useful since password field won't be displayed in the form.
	# password = ReadOnlyPasswordHashField()
	
	# set email field as disabled & readonly so user won't be able to interact with it
	# this also sets some desired styles from Bootstrap

	# setting readonly on a widget only makes the input in the browser read-only.  do this "https://stackoverflow.com/a/331550" to ensure its value doesn't change on form level.  P.S. I can also do this by passing the user object to the form and setting the initial attribute of the field to the user's email.
	email = forms.EmailField(
		label=_('Email address'),
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
		else:
			return self.cleaned_data['email']

	# def clean_password(self):
	# 	# Regardless of what the user provides, return the initial value.
	# 	# This is done here, rather than on the field, because the
	# 	# field does not have access to the initial value
	# 	return self.initial["password"]


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
		"""Checks that no two numbers are the same and that there should be at least one number that supports Whatsapp."""
		if any(self.errors):
			# don't bother validating the formset if there are already errors in any of its forms
			return

		# at least one form should be present
		assert (n := len(self.forms)) >= 1, "At least one form must be present, got {}".format(n)

		numbers_list = []
		can_whatsapp_list = []
		for form in self.forms:
			if self.can_delete and self._should_delete_form(form):
				continue

			number = form.cleaned_data.get('number')
			if number in numbers_list:
				raise ValidationError(_("Phone numbers should be unique."))
			numbers_list.append(number)
			can_whatsapp_list.append(form.cleaned_data.get('can_whatsapp'))

		# if there isn't any number that supports whatsapp, raise error 
		# also perform this check in frontend
		if not any(can_whatsapp_list):
			raise ValidationError(_("Enter at least one number that supports WhatsApp."))


# PhoneNumberFormset = generic_inlineformset_factory(
# 	PhoneNumber, 
# 	form=PhoneNumberForm, 
# 	formset=BasePhoneNumberFormset, 
# 	extra=1
# )

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
