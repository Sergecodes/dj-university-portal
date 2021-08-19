from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Fieldset, Field
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import SocialProfile, SocialMediaFollow


class SocialMediaFollowForm(forms.ModelForm):

	class Meta:
		model = SocialMediaFollow
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.helper.disable_csrf = True
		self.helper.form_tag = False
		self.helper.layout = Layout(
			Fieldset(_('Social Media Presence'),
				Row(
					Column(
						PrependedText(
							'facebook_follow', 
							'<i class="fab fa-facebook-f link-primary"></i>', 
						),
						css_class='form-group col-md-6 col-lg-4 mb-0'
					),
					Column(
						PrependedText(
							'twitter_follow', 
							'<i class="fab fa-twitter link-primary"></i>',
						),
						css_class='form-group col-md-6 col-lg-4 mb-0'
					),
					Column(
						PrependedText(
							'instagram_follow', 
							'<i class="fab fa-instagram link-danger"></i>', 
						),
						css_class='form-group col-md-6 col-lg-4 mb-0'
					),
					css_class='form-row'
				),
				css_class='mb-2'
			),
		)


class SocialProfileForm(forms.ModelForm):
	
	class Meta:
		model = SocialProfile
		exclude = ('user', 'social_media', )
		widgets = {
			'department': forms.TextInput(
				attrs={'placeholder': _('Ex. Mathematics')}
			),
			'profile_image': forms.FileInput(),
			'birth_date': forms.DateInput(attrs={'type': 'date'}),
			'about_me': forms.Textarea(attrs={'rows': '4'}),
			'hobbies': forms.Textarea(attrs={'rows': '4'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['school'].empty_label = None
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
			Field('is_visible', css_class='mb-2')
		)
