from ckeditor.widgets import CKEditorWidget
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
	Layout, LayoutObject, Row, Column, Fieldset, 
	MultiField, HTML, Div, ButtonHolder, TEMPLATE_PACK,
	Button, Hidden, Reset, Submit, Field
)
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
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

	template = 'marketplace/basic_upload.html'
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

	institution = forms.ModelChoiceField(
		queryset=Institution.objects.all(), 
		empty_label=None
	)
	description = forms.CharField(
		widget= CKEditorWidget(config_name='demo'),
		help_text=_("Describe the item you're selling and provide complete and accurate 		details. Use a clear and concise format to keep your description lisible.")
	)
	category = forms.ModelChoiceField(
		label=_('Category'),
		queryset=ItemCategory.objects.all(), 
		empty_label=None,
		widget=forms.Select(attrs={'class': 'js-category'})  # add this class
	)
	
	# initially, it should contain the sub categories of the current(initial) selected parent category. also some user's listings might not have sub categories
	sub_category = forms.ModelChoiceField(
		label=_('Sub category'), 
		# initially set to empty queryset
		# a call will be made via ajax which will set this queryset based on the value of the parent category
		queryset=ItemSubCategory.objects.none(), 
		required=False,
		widget=forms.Select(attrs={'class': 'js-subcategory'})
	)
	# condition = forms.ChoiceField(
	# 	choices=CONDITIONS,
	# 	widget=forms.Select(attrs={'class': 'js-condition'})
	# )

	# queryset will be obtained from user's list of phone number, defined in form's __init__ method
	contact_numbers = forms.ModelMultipleChoiceField(
		queryset=None, 
		required=True,
		widget=forms.CheckboxSelectMultiple()
	)

	def __init__(self, *args, **kwargs):
		# Do not use kwargs.pop('user', None) due to potential security loophole (the user object must be in the form!)
		self.user = kwargs.pop('user')
		user = self.user

		super().__init__(*args, **kwargs)

		# email used for notifications concerning listing is user's email by default.
		# user may enter another email
		self.fields['contact_email'].initial = user.email
		self.fields['contact_name'].initial = user.full_name
		# self.fields['condition'].initial = ''
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
			),
			Fieldset(_('Listing Details'),
				'title',
				Row(
					Column('condition', css_class='form-group col-md-4 mb-0'),
					Column('condition_description', css_class='form-group col-md-8 mb-0'),
					css_class='form-row'
				),
				# photo upload functionality here
				PhotoFormLayout(
					# todo, definitely change this queryset! 
					extra_context={'photos': ItemListingPhoto.objects.all()}
				),  
				'description',  
				# 'price',
				Field('price', step='500')
			),
			Fieldset(_("Seller's Information"),
				'contact_email',
				'contact_name',
				'contact_numbers'
			),
			# insert original_language as hidden field.
			# Submit('submit', _('List item'), css_class='btn btn-primary'),
			FormActions(
				Submit('submit', _('List item'), css_class='btn-lg me-5'),
				Button('preview', _('Preview'), css_class='btn-lg btn-secondary')
			)
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
			'condition_description': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
		}
	

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
 
ItemListingPhotoFormset = inlineformset_factory(
	ItemListing,
	ItemListingPhoto,
	form=ItemListingPhotoForm, 
	extra=3
)