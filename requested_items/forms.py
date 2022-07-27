from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
	Layout, Row, Column,
	Fieldset, HTML, Submit
)
from django import forms
from django.utils.translation import gettext_lazy as _

from core.constants import EXTERNAL_LINK_ICON
from core.forms import PhotoFormLayout
from core.models import City, Country
from core.utils import get_edit_profile_url, PhotoUploadMixin, get_country
from .models import RequestedItem, RequestedItemPhoto


class RequestedItemPhotoForm(forms.ModelForm, PhotoUploadMixin):
	class Meta:
		model = RequestedItemPhoto
		fields = ('file', )


class RequestedItemForm(forms.ModelForm):
	country = forms.ModelChoiceField(
		queryset=Country.objects.all(),
		empty_label=None,
	)
	city = forms.ModelChoiceField(
		queryset=None, 
		empty_label=None
	)
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
		update, country_or_code = kwargs.pop('update', False), kwargs.pop('country_or_code')
		super().__init__(*args, **kwargs)

		country = get_country(country_or_code)

		# email used for notifications concerning listing is user's email by default.
		# user may enter another email
		self.fields['contact_email'].initial = user.email
		self.fields['contact_numbers'].queryset = user.phone_numbers.all()
		self.fields['country'].initial = country.pk
		self.fields['city'].queryset = City.objects.filter(country=country)
		self.fields['category'].empty_label = None

		self.helper = FormHelper()
		self.helper.layout = Layout(
			Fieldset(_('Area & Item Category'),
				Row(
					Column('country', css_class='form-group col-md-6'),
					Column('city', css_class='form-group col-md-6'),
					Column('category', css_class='form-group'),
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
					class='btn btn-outline link-success opacity-75 d-inline-block mb-4 pt-0' \
					href=" + get_edit_profile_url(user) + '?next={{ request.get_full_path }}#phoneSection>'
					+ str(_('Edit phone numbers')) + EXTERNAL_LINK_ICON + 
				"</a>"
			),
		)

		if update:
			self.helper.add_input(Submit('submit', _('Update'), css_class="d-block btn-success"))
		else:
			self.helper.add_input(Submit('submit', _('Post'), css_class="d-block btn-success"))



