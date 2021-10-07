from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Row, Column, Fieldset
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import SocialProfile, SocialMediaFollow


class SocialMediaFollowForm(forms.ModelForm):

	class Meta:
		model = SocialMediaFollow
		fields = '__all__'
		widgets = {
			'website_follow': forms.TextInput(attrs={
				'placeholder': _('www.site1.com; www.site2.com')
			})
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.helper = FormHelper()
		# remove auto-included csrf token.  will manually include it.
		self.helper.disable_csrf = True
		self.helper.form_tag = False
		self.helper.layout = Layout(
			Fieldset(_('Social Media*'),
				HTML(" \
					<div \
						class='form-text text-muted mb-3' \
					>" +  str(_('Add at least one social account')) +
					"</div>"
				),
				Row(
					Column(
						PrependedText(
							'email', 
							'<i class="far fa-envelope fs-5 link-danger"></i>', 
						),
						css_class='form-group col-sm-6 col-lg-4 mb-0'
					),
					Column(
						PrependedText(
							'facebook_follow', 
							'<i class="fab fa-facebook-f link-primary"></i>', 
						),
						css_class='form-group col-sm-6 col-lg-4 mb-0'
					),
					Column(
						PrependedText(
							'twitter_follow', 
							'<i class="fab fa-twitter link-primary"></i>',
						),
						css_class='form-group col-sm-6 col-lg-4 mb-0'
					),
					Column(
						PrependedText(
							'instagram_follow', 
							'<i class="fab fa-instagram fa-lg link-danger"></i>', 
						),
						css_class='form-group col-sm-6 col-lg-4 mb-0'
					),
					Column(
						PrependedText(
							'tiktok_follow', 
							'<i class="fab fa-tiktok"></i>', 
						),
						css_class='form-group col-sm-6 col-lg-4 mb-0'
					),
					Column(
						PrependedText(
							'github_follow', 
							'<i class="fab fa-github fa-lg"></i>', 
						),
						css_class='form-group col-sm-6 col-lg-4 mb-0'
					),
					Column(
						PrependedText(
							'website_follow', 
							'<i class="fas fa-link"></i>', 
						),
						css_class='form-group col-sm-10 mb-0'
					),
					css_class='form-row'
				),
				css_class='mb-2'
			),
		)

	def clean(self):
		## user should enter at least one social media value..
		data = self.cleaned_data

		# list that contains boolean values for each social media platform
		boolean_list = []

		for platform, value in data.items():
			# first remove all white space in string 
			# (eg in case user enters and submits white space only)
			# remember though that django form charfields have a strip property which is by default True
			# it enables removal of whitespace before and after the field's value
			# nonetheless, we need this check..
			# value will be None if nothing is entered, convert it to an empty string in that case
			value = '' if value == None else value
			value = value.replace(' ', '')
			boolean_list.append(bool(value))
		
		# ensure at least one social media link is present
		if not any(boolean_list):
			self.add_error(
				None, 
				_('At least one social media account must be added.')
			)
		
		return data


class SocialProfileForm(forms.ModelForm):
	# add bootstrap5 form field error class.
	# error_css_class = 'is-invalid'
	# field_order = []
	
	class Meta:
		model = SocialProfile
		exclude = ('user', 'social_media', 'original_language', 'last_modified', 'view_count', )
		widgets = {
			'department': forms.TextInput(
				attrs={'placeholder': _('Ex. Mathematics')}
			),
			# set input to file input so as to activate `crispy form` magic
			'profile_image': forms.FileInput(),
			'birth_date': forms.DateInput(attrs={'type': 'date'}),
			'about_me': forms.Textarea(attrs={'rows': '4'}),
			'hobbies': forms.Textarea(attrs={'rows': '4'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)	

		self.helper = FormHelper()
		self.helper.disable_csrf = True
		self.helper.form_tag = False
		self.helper.layout = Layout(
			Fieldset(_('Schooling Information'),
				Row(
					Column('school', css_class='form-group col-md-6 mb-0'),
					Column('level', css_class='form-group col-md-6 mb-0'),
					Column('department', css_class='col-md-6 mb-0'),
					css_class='form-row'
				),
				css_class='mb-2'
			),
			Fieldset(_('Personal Information'),
				Row(
					Column('gender', css_class='form-group col-md-6 mb-0'),
					Column('birth_date', css_class='form-group col-md-6 mb-0'),
					Column('profile_image', css_class='form-group col-md-6 mb-0'),
					css_class='form-row'
				),
				css_class='mb-2'
			),
			Fieldset(_("Additional Information"),
				Row(
					Column('current_relationship', css_class='form-group col-md-6 mb-0'),
					Column('interested_relationship', css_class='form-group col-md-6 mb-0'),
					Column('about_me', css_class='form-group col-md-6 mb-0'),
					Column('hobbies', css_class='form-group col-md-6 mb-0'),
					css_class='form-row'
				),
				css_class='mb-2'
			),
			# Field('is_visible', css_class='mb-2')
		)
