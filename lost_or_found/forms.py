from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
	Layout, Row, Column,
	Fieldset, HTML, Submit
)
from django import forms
from django.utils.translation import gettext_lazy as _

from core.constants import EXTERNAL_LINK_ICON
from core.forms import PhotoFormLayout
from core.models import Country, City
from core.utils import get_edit_profile_url, PhotoUploadMixin, get_country
from .models import LostItem, LostItemPhoto, FoundItem


class LostItemPhotoForm(forms.ModelForm, PhotoUploadMixin):
	class Meta:
		model = LostItemPhoto
		fields = ('file', )


class LostItemForm(forms.ModelForm):
	contact_numbers = forms.ModelMultipleChoiceField(
		queryset=None, 
		required=True,
		widget=forms.CheckboxSelectMultiple()
	)
	country = forms.ModelChoiceField(
		queryset=Country.objects.all(),
		empty_label=None,
		widget=forms.Select(attrs={'class': 'js-country'})
	)
	city = forms.ModelChoiceField(
		queryset=None, 
		empty_label=None,
		widget=forms.Select(attrs={'class': 'js-city'})
	)

	class Meta:
		model = LostItem
		exclude = (
			'slug', 'slug_en', 'slug_fr', 'posted_datetime', 'last_modified', 
			'poster', 'original_language', 'view_count'
		)
		widgets = {
			'item_lost': forms.TextInput(attrs={'placeholder': _('iPhone 13')}),
			'area_lost': forms.TextInput(attrs={'placeholder': _("Beside St. Peter's Chapel")}),
			'how_lost': forms.Textarea(attrs={
				'placeholder': _('After the Sunday service, i forgot my phone on the bench near the door then...'),
				'rows': '4',
			}),
			'bounty': forms.TextInput(attrs={'placeholder': _('$100 to the person who will return my phone to me')}),
			'item_description': forms.Textarea(attrs={'placeholder': _('The phone has a black case and ...'), 'rows': '4'})
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

		self.helper = FormHelper()
		self.helper.layout = Layout(
			Fieldset(_('Lost Item Information'),
				Row(
					Column('country', css_class='form-group col-md-6'),
					Column('city', css_class='form-group col-md-6'),
					css_class='form-row'
				),
				'item_lost',
				'item_description',
				PhotoFormLayout(extra_context={
					'form_for': 'lost_item', 
					'upload_help_text': _("Upload maximum 3 photos of the lost item. Allow this empty if you do not have any photos."),
					'initial_photos': initial_photos
				}),  
				'area_lost',
				'how_lost',
				'bounty',
				css_class='mb-2'
			),
			Fieldset(_("Poster's Information"),
				'contact_email',
				'contact_numbers'
			),
			# modal button to trigger button used in the template.
			# this button isn't inserted directly in the template so as to maintain the position/layout of elements
			HTML(" \
				<a \
					class='btn btn-outline link-success opacity-75 d-inline-block mb-4 pt-0' \
					href=" + get_edit_profile_url(user) + '?next={{ request.get_full_path }}#phoneSection>'
					+ str(_('Edit phone numbers')) + EXTERNAL_LINK_ICON + 
				"</a>"
			),
			HTML(" \
				<p class='alert alert-warning'>" \
					+ str(_(
						'If anyone says this item belongs to them, verify '
						'that they are saying the truth by asking them questions '
						'concerning the item; such as a detailed description of the item.'
					)) +
				"</p>"
			),
		)

		if update:
			self.helper.add_input(Submit('submit', _('Update'), css_class="d-block btn-success"))
		else:
			self.helper.add_input(Submit('submit', _('Report item'), css_class="d-block btn-success"))


class FoundItemForm(forms.ModelForm):
	contact_numbers = forms.ModelMultipleChoiceField(
		queryset=None, 
		required=True,
		widget=forms.CheckboxSelectMultiple()
	)
	country = forms.ModelChoiceField(
		queryset=Country.objects.all(),
		empty_label=None,
		widget=forms.Select(attrs={'class': 'js-country'})
	)
	city = forms.ModelChoiceField(
		queryset=None, 
		empty_label=None,
		widget=forms.Select(attrs={'class': 'js-city'})
	)

	class Meta: 
		model = FoundItem
		exclude = (
			# we include slug_en and slug_fr coz with `modeltranslation`,
			# doing something like obj.slug_en = 'foo' also does obj.slug = 'foo'
			# now if we don't exclude them, their values will be '' (obj.slug_en = '').
			# so the object will be saved as obj.slug = ''
			'slug', 'slug_en', 'slug_fr', 'posted_datetime', 'last_modified', 
			'poster', 'original_language', 'view_count'
		)
		widgets = {
			'item_found': forms.TextInput(attrs={'placeholder': _('Green backpack')}),
			'area_found': forms.TextInput(attrs={'placeholder': _('Infront of the Foden Hotel')}),
			'how_found': forms.Textarea(attrs={
				'placeholder': _(
					'I was walking near the hotel and found the green backpack ...'
				),
				'rows': '4',
			}),
		}

	def __init__(self, *args, **kwargs):
		user, update = kwargs.pop('user'), kwargs.pop('update', False)
		country_or_code = kwargs.pop('country_or_code')
		super().__init__(*args, **kwargs)

		country = get_country(country_or_code)

		# email used for notifications concerning listing is user's email by default.
		# user may enter another email
		self.fields['contact_email'].initial = user.email
		self.fields['contact_numbers'].queryset = user.phone_numbers.all()
		self.fields['country'].initial = country.pk
		self.fields['city'].queryset = City.objects.filter(country=country)

		self.helper = FormHelper()
		self.helper.layout = Layout(
			Fieldset(_('Found Item Information'),
				Row(
					Column('country', css_class='form-group col-md-6'),
					Column('city', css_class='form-group col-md-6'),
					css_class='form-row'
				),
				'item_found',
				'area_found',
				'how_found',
				css_class='mb-2'
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
			self.helper.add_input(Submit('submit', _('Report item'), css_class="d-block btn-success"))
