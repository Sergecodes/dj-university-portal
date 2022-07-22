from ckeditor.widgets import CKEditorWidget
from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
	Layout, Row, Column,
	Fieldset, HTML, Submit
)
from django import forms
from django.utils.translation import gettext_lazy as _

from core.constants import EXTERNAL_LINK_ICON
from core.forms import PhotoFormLayout
from core.models import Institution
from core.utils import get_edit_profile_url, PhotoUploadMixin
from .models import (
	ItemListing, AdListing, ItemSubCategory,
	ItemCategory, ItemListingPhoto, AdListingPhoto
)


class ItemListingPhotoForm(forms.ModelForm, PhotoUploadMixin):
	class Meta:
		model = ItemListingPhoto
		fields = ('file', )


class ItemListingForm(forms.ModelForm):
	"""Form used to create a new item listing."""
	# slug = forms.CharField(required=False)
	school = forms.ModelChoiceField(
		queryset=None, 
		empty_label=None
	)
	description = forms.CharField(
		widget= CKEditorWidget(config_name='listing_description'),
		help_text=_("Describe the item you're selling and provide complete and accurate details. <br> Use a clear and concise format to keep your description lisible.")
	)
	category = forms.ModelChoiceField(
		queryset=ItemCategory.objects.all(), 
		empty_label=None,
		# this class will be used in js script
		widget=forms.Select(attrs={'class': 'js-category'})  
	)
	# initially, it should contain the sub categories of the current(initial) selected parent category
	# also some user's listings might not have sub categories
	sub_category = forms.ModelChoiceField(
		required=False,
		queryset=ItemSubCategory.objects.none(),
		widget=forms.Select(attrs={'class': 'js-subcategory'})
	)
	price = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Ex. 150 000'}),
	)

	# queryset will be obtained from user's list of phone number, defined in form's __init__ method
	# so for now set it to None
	contact_numbers = forms.ModelMultipleChoiceField(
		queryset=None, 
		required=True,
		widget=forms.CheckboxSelectMultiple()
	)

	class Meta:
		model = ItemListing
		exclude = ('poster', 'slug', 'slug_en', 'slug_fr', 'original_language', 'view_count', )
		help_texts = {
			'title': _("A descriptive title helps buyers find your item. State exactly what your 			item is. <br> Include words that buyers will use to search for your item"),
			'condition': _("Select the condition of the item you're listing."),
		}
		widgets = {
			'condition': forms.Select(attrs={'class': 'js-condition'}),
			'condition_description': forms.Textarea(
				attrs={'rows': 5, 'cols': 40, 'class': 'js-condition-description'}
			),
		}

	def __init__(self, *args, **kwargs):
		# Do not use kwargs.pop('user', None) due to potential security loophole (the user object must be in the form!)
		user, initial_photos = kwargs.pop('user'), kwargs.pop('initial_photos', [])
		update = kwargs.pop('update', False)
		super().__init__(*args, **kwargs)

		# email used for notifications concerning listing is user's email by default.
		# user may enter another email
		self.fields['contact_email'].initial = user.email
		self.fields['contact_numbers'].queryset = user.phone_numbers.all()
		self.fields['school'].queryset = Institution.objects.filter(country=user.country_id)
		
		self.helper = FormHelper()
		self.helper.layout = Layout(
			Fieldset(_('School & Item Category'),
				'school',
				Row(
					Column('category', css_class='form-group col-md-6 mb-0'),
					Column('sub_category', css_class='form-group col-md-6 mb-0'),
					css_class='form-row'
				),
				css_class='mb-2'
			),
			Fieldset(_('Listing Details'),
				'title',
				# 'duration',
				Row(
					Column('condition', css_class='form-group col-md-5 mb-0'),
					Column('condition_description', css_class='form-group col-md-7 mb-0'),
					css_class='form-row'
				),
				# photo upload template here
				PhotoFormLayout(extra_context={
					'form_for': 'item_listing', 
					'upload_help_text': _('Upload at least 3 photos and at most 8 photos.'),
					'initial_photos': initial_photos
				}),  
				'description',
				AppendedText('price', 'FCFA'),
				css_class='mb-2'
			),
			Fieldset(_("Seller's Information"),
				'contact_email',
				'contact_numbers'
			),
			# modal button to trigger button used in the template.
			# this button isn't inserted directly in the template 
			# so as to maintain the position/layout of elements

			# remove modal since unload listener is used...
			HTML(" \
				<a \
					class='btn btn-outline link-success opacity-75 d-inline-block mb-4 pt-0' \
					href=" + get_edit_profile_url(user) + '?next={{ request.get_full_path }}#phoneSection>'
					+ str(_('Edit phone numbers')) + EXTERNAL_LINK_ICON + 
				"</a>"
			),
			# no submit button inserted so as to use same form (different values for the submit button)
			# for create and update forms (eg List Item vs Update Item)
		)

		# if i insert the submit button via the html template, it will be out of the form.
		if update:
			self.helper.add_input(Submit('submit', _('Update item'), css_class="d-block btn-lg btn-success"))
		else:
			self.helper.add_input(Submit('submit', _('Post item'), css_class="d-block btn-lg btn-success"))

	def clean_price(self):
		"""Price should contain only spaces and digits. """
		# 0 is in string since the following split() method works on strings
		price = self.cleaned_data.get('price', '0')  

		# remove all whitespace from price
		price = ''.join(price.split())

		# price should now contain only digits
		if not price.isdigit():
			self.add_error(
				'price', 
				_('The price you entered is invalid. Prices may contain only spaces and digits.')
			)
		else:
			return int(price)


class AdListingPhotoForm(forms.ModelForm, PhotoUploadMixin):
	class Meta:
		model = AdListingPhoto
		fields = ('file', )


class AdListingForm(forms.ModelForm):
	description = forms.CharField(
		widget= CKEditorWidget(config_name='listing_description'),
		help_text=_("Describe your advert. Use a clear and concise format to keep your description lisible.")
	)
	school = forms.ModelChoiceField(
		queryset=None, # queryset will be set in form init
		empty_label=None
	)
	# queryset will be obtained from user's list of phone number, defined in form's __init__ method
	contact_numbers = forms.ModelMultipleChoiceField(
		queryset=None, 
		required=True,
		widget=forms.CheckboxSelectMultiple()
	)

	class Meta:
		model = AdListing
		exclude = ('poster', 'slug', 'slug_en', 'slug_fr', 'original_language', 'view_count', )
		help_texts = {
			'title': _("A descriptive title helps others easily find your advert. <br> Include words that others will use to search for your advert"),
		}
		widgets = {
			'pricing': forms.TextInput(attrs={'placeholder': _('Ex. 10,000F per unit')})
		}

	def __init__(self, *args, **kwargs):
		user, initial_photos = kwargs.pop('user'), kwargs.pop('initial_photos', [])
		update = kwargs.pop('update', False)
		super().__init__(*args, **kwargs)

		# email used for notifications concerning listing is user's email by default.
		# user may enter another email
		self.fields['contact_email'].initial = user.email
		self.fields['contact_numbers'].queryset = user.phone_numbers.all()
		self.fields['school'].queryset = Institution.objects.filter(country=user.country_id)
		self.fields['category'].empty_label = None

		self.helper = FormHelper()
		self.helper.layout = Layout(
			Fieldset(_('School & Advert Category'),
				Row(
					Column('school', css_class='form-group col-md-6 mb-0'),
					Column('category', css_class='form-group col-md-6 mb-0'),
					css_class='form-row'
				),
				css_class='mb-2'
			),
			Fieldset(_('Listing Details'),
				'title',
				# 'duration',
				# photo upload template here
				PhotoFormLayout(extra_context={
					'form_for': 'ad_listing', 
					'upload_help_text': _("It isn't obligatory to post a photo."),
					'initial_photos': initial_photos
				}),  
				'description',
				'pricing',
				css_class='mb-2'
			),
			Fieldset(_("Seller's Information"),
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
			self.helper.add_input(Submit('submit', _('Update advert'), css_class="d-block btn-lg btn-success"))
		else:
			self.helper.add_input(Submit('submit', _('Post advert'), css_class="d-block btn-lg btn-success"))

