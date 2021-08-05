import re
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
from django.urls.base import set_urlconf
from django.utils.translation import ugettext_lazy as _

from .models import (
	ItemListing, Ad, Institution, ItemSubCategory,
	ItemCategory, ItemListingPhoto
)


class PhotoFormLayout(LayoutObject):
	""" 
	Render the the photo upload template, as though it were a Field.
	Accepts the names (as a string) of template to use.
	Used to insert item listing & ad photo upload templates into their respective forms.

	Examples:
		PhotoFormLayout('photo_form')
		PhotoFormLayout('photo_form', template='...')
		PhotoFormLayout('photo_form', template='...', extra_context={...})
	"""

	template = 'marketplace/photos_upload.html'
	extra_context = {}

	def __init__(self, template=None, *args, **kwargs):
		# retrieve and store extra context
		self.extra_context = kwargs.pop('extra_context', self.extra_context)

		# Override class variable with an instance level variable
		if template:
			# print(template)
			self.template = template
		
	def render(self, form, form_style, context, **kwargs):
		if self.extra_context:
			context.update(self.extra_context)

		return render_to_string(self.template, context.flatten())


class ItemListingPhotoForm(forms.ModelForm):

	class Meta:
		model = ItemListingPhoto
		fields = ('file', )


class ItemListingForm(forms.ModelForm):
	"""Form used to create a new item listing."""
	# mark slug as not required so it doesn't hinder form validation
	slug = forms.CharField(required=False)
	institution = forms.ModelChoiceField(
		queryset=Institution.objects.all(), 
		empty_label=None
	)
	description = forms.CharField(
		widget= CKEditorWidget(config_name='demo'),
		help_text=_("Describe the item you're selling and provide complete and accurate details. <br> Use a clear and concise format to keep your description lisible.")
	)
	category = forms.ModelChoiceField(
		queryset=ItemCategory.objects.all(), 
		empty_label=None,
		widget=forms.Select(attrs={'class': 'js-category'})  # add this class
	)
	# initially, it should contain the sub categories of the current(initial) selected parent category. also some user's listings might not have sub categories
	sub_category = forms.ModelChoiceField(
		required=False,
		queryset=ItemSubCategory.objects.all(),
		widget=forms.Select(attrs={'class': 'js-subcategory'})
	)
	price = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Ex. 150 000'}),
	)

	# queryset will be obtained from user's list of phone number, defined in form's __init__ method
	contact_numbers = forms.ModelMultipleChoiceField(
		queryset=None, 
		required=True,
		widget=forms.CheckboxSelectMultiple()
	)

	class Meta:
		model = ItemListing
		exclude = ('owner', )
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
		user = kwargs.pop('user')

		super().__init__(*args, **kwargs)

		external_link_svg = ' \
			<svg x="0px" y="0px" viewBox="0 0 100 100" width="15" height="15" class=""> \
				<path fill="currentColor" d="M18.8,85.1h56l0,0c2.2,0,4-1.8,4-4v-32h-8v28h-48v-48h28v-8h-32l0,0c-2.2,0-4,1.8-4,4v56C14.8,83.3,16.6,85.1,18.8,85.1z" style="--darkreader-inline-fill:currentColor;" data-darkreader-inline-fill=""> \
				</path> \
				<polygon fill="currentColor" points="45.7,48.7 51.3,54.3 77.2,28.5 77.2,37.2 85.2,37.2 85.2,14.9 62.8,14.9 62.8,22.9 71.5,22.9" style="--darkreader-inline-fill:currentColor;" data-darkreader-inline-fill=""> \
				</polygon> \
			</svg>'

		# email used for notifications concerning listing is user's email by default.
		# user may enter another email
		self.fields['contact_email'].initial = user.email
		self.fields['contact_name'].initial = user.full_name
		self.fields['contact_numbers'].queryset = user.phone_numbers.all()

		self.helper = FormHelper()
		self.helper.layout = Layout(
			Fieldset(_('Institution & Item Category'),
				'institution',
				Row(
					Column('category', css_class='form-group col-md-6 mb-0'),
					Column('sub_category', css_class='form-group col-md-6 mb-0'),
					css_class='form-row'
				),
				css_class='mb-2'
			),
			Fieldset(_('Listing Details'),
				'title',
				'duration',
				Row(
					Column('condition', css_class='form-group col-md-5 mb-0'),
					Column('condition_description', css_class='form-group col-md-7 mb-0'),
					css_class='form-row'
				),
				# photo upload template here
				PhotoFormLayout(extra_context={}),  
				'description',
				'price',
				css_class='mb-2'
			),
			Fieldset(_("Seller's Information"),
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
				>" +  str(_('Edit phone numbers')) + external_link_svg + 
				"</button>"
			),
			# insert original_language as hidden field.
			HTML('<input type="hidden" name="original_language" value="{{ LANGUAGE_CODE }}" />'),
			FormActions(
				Submit('submit', _('List item'), css_class='btn-lg me-5'),
				Button('preview', _('Preview'), css_class='btn-lg btn-secondary')
			)
		)

	def clean_price(self):
		"""Price should contain only spaces and digits. """
		price = self.cleaned_data.get('price', '0')  # 0 is in string since the following split() method works on strings

		# remove all whitespace from price
		price = ''.join(price.split())

		# price should now contain only digits
		if not price.isdigit():
			self.add_error('price', _('The price you entered is invalid. Prices may contain only spaces and digits.'))
		else:
			return int(price)


'''
class ItemListingUpdateForm(forms.ModelForm):
	"""A form for updating item listings."""
	
	class Meta:
		model = ItemListing
		fields = ['email', 'full_name', 'username', 'first_language', 'gender', ]
		widgets = {
			'first_language': forms.RadioSelect,
			'gender': forms.RadioSelect,
		}
'''
 