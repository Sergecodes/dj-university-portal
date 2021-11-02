from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
	Layout, Row, Column,
	Fieldset, HTML, Submit
)
from django import forms
from django.utils.translation import gettext_lazy as _

from core.constants import EXTERNAL_LINK_ICON
from core.forms import PhotoFormLayout
from core.utils import get_edit_numbers_url
from .models import RequestedItem, RequestedItemPhoto


class RequestedItemPhotoForm(forms.ModelForm):
	class Meta:
		model = RequestedItemPhoto
		fields = ('file', )


class RequestedItemForm(forms.ModelForm):
	contact_numbers = forms.ModelMultipleChoiceField(
		queryset=None, 
		required=True,
		widget=forms.CheckboxSelectMultiple()
	)

	class Meta:
		model = RequestedItem
		exclude = (
			'slug', 'slug_en', 'slug_fr', 'posted_datetime', 'last_modified', 
			'poster', 'original_language', 'view_count', 
		)
		widgets = {
			'item_requested': forms.TextInput(attrs={'value': _('Looking for ...')}),
			'item_description': forms.Textarea(attrs={'rows': '3'})
		}

	def __init__(self, *args, **kwargs):
		user, initial_photos = kwargs.pop('user'), kwargs.pop('initial_photos', [])
		update = kwargs.pop('update', False)
		super().__init__(*args, **kwargs)

		# email used for notifications concerning listing is user's email by default.
		# user may enter another email
		self.fields['contact_email'].initial = user.email
		self.fields['contact_numbers'].queryset = user.phone_numbers.all()
		self.fields['category'].empty_label = None

		self.helper = FormHelper()
		self.helper.layout = Layout(
			Fieldset(_('School & Item Category'),
				Row(
					Column('school', css_class='form-group col-md-6 mb-0'),
					Column('category', css_class='form-group col-md-6 mb-0'),
					css_class='form-row'
				),
				css_class='mb-2'
			),
			Fieldset(_('Requested Item Information'),
				'item_requested',
				'item_description',
				PhotoFormLayout(extra_context={
					'form_for': 'requested_item', 
					'upload_help_text': _("Upload maximum 3 photos of your requested item. Allow this empty if you do not have any photos."),
					'initial_photos': initial_photos
				}),  
                'price_at_hand'
			),
			Fieldset(_("Poster's Information"),
				'contact_email',
				'contact_numbers'
			),
			HTML(" \
				<a \
					class='btn btn-outline link-primary d-inline-block mb-4 pt-0' \
					href=" + get_edit_numbers_url(user) + '>'
					+ str(_('Edit phone numbers')) + EXTERNAL_LINK_ICON + 
				"</a>"
			),
		)

		if update:
			self.helper.add_input(Submit('submit', _('Update'), css_class="d-block"))
		else:
			self.helper.add_input(Submit('submit', _('Post'), css_class="d-block"))



