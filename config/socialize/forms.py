from ckeditor.widgets import CKEditorWidget
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
	Layout, LayoutObject, Row, Column, Fieldset, 
	MultiField, HTML, Div, ButtonHolder,
	Button, Hidden, Reset, Submit, Field
)
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from .models import SocialProfile


class SocialProfileForm(forms.ModelForm):
	pass

	class Meta:
		exclude = ('user', )

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.helper.layout = Layout(
			Row(
				Column('category', css_class='form-group col-md-6 mb-0'),
				Column('sub_category', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Fieldset(_("Seller's Information"),
				'contact_email',
				'contact_name',
				'contact_numbers'
			),
			# insert original_language as hidden field.
			HTML('<input type="hidden" name="original_language" value="{{ LANGUAGE_CODE }}" />'),
			Submit('submit', _('List item'), css_class='btn-lg d-block'),
		)


