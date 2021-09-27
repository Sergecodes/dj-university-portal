from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from core.constants import EXTERNAL_LINK_ICON
from core.forms import PhotoFormLayout
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
		exclude = ('slug', 'posted_datetime', 'last_modified', 'poster', 'original_language',)
		widgets = {
			'item_requested': forms.TextInput(attrs={'value': _('Looking for ...')}),
			'item_description': forms.Textarea(attrs={'rows': '3'})
		}

	def __init__(self, *args, **kwargs):
		user, initial_photos = kwargs.pop('user'), kwargs.pop('photos', [])
		super().__init__(*args, **kwargs)

		# email used for notifications concerning listing is user's email by default.
		# user may enter another email
		self.fields['contact_email'].initial = user.email
		self.fields['contact_name'].initial = user.full_name
		self.fields['contact_numbers'].queryset = user.phone_numbers.all()
		self.fields['school'].empty_label = None

		self.helper = FormHelper()
		self.helper.layout = Layout(
			Fieldset(_('Requested Item Information'),
				'school',
				'item_requested',
				'item_description',
				PhotoFormLayout(extra_context={
					'form_for': 'requested_item', 
					'upload_help_text': _("Upload maximum 3 photos of your requested item. Allow this empty if you do not have any photos."),
					'photos': initial_photos
				}),  
                'price_at_hand'
			),
			Fieldset(_("Poster's Information"),
				'contact_email',
				'contact_name',
				'contact_numbers'
			),
			# modal button to trigger button used in the template.
			# this button isn't inserted directly in the template so as to maintain the position/layout of elements
			HTML(" \
				<button \
					class='btn btn-outline text-primary d-inline-block mb-4 pt-0' \
					type='button' \
					data-bs-toggle='modal' \
					data-bs-target='#leavePageModal' \
				>" +  str(_('Edit phone numbers')) + EXTERNAL_LINK_ICON + "</button>"
			),
			Submit('submit', _('Post'), css_class='d-block'),
		)


