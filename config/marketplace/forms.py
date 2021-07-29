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
	ItemListing, Ad, Institution, ItemCategory,
	ItemParentCategory, ItemListingPhoto
)

# see https://stackoverflow.com/a/43549692
class Formset(LayoutObject):
	""" 
	Renders an entire formset, as though it were a Field.
	Accepts the names (as a string) of formset and helper as they
	are defined in the context

	Examples:
		Formset('contact_formset')
		Formset('contact_formset', 'contact_formset_helper')
	"""

	# template = "%s/formset.html" % TEMPLATE_PACK
	template = 'marketplace/formset.html'

	def __init__(self, formset_context_name, helper_context_name=None, template=None, label=None):
		self.formset_context_name = formset_context_name
		self.helper_context_name = helper_context_name

		# crispy_forms/layout.py:302 requires us to have a fields property
		self.fields = []

		# Overrides class variable with an instance level variable
		if template:
			print(template)
			self.template = template

	def render(self, form, form_style, context, **kwargs):
		formset = context.get(self.formset_context_name)
		helper = context.get(self.helper_context_name)
		# closes form prematurely if this isn't explicitly stated
		if helper:
			helper.form_tag = False

		context.update({'formset': formset, 'helper': helper})
		return render_to_string(self.template, context.flatten())


class ItemListingPhotoForm(forms.ModelForm):
	image = forms.ImageField(label=_('Photo'))

	class Meta:
		model = ItemListingPhoto
		fields = ('image', )


class ItemListingForm(forms.ModelForm):
	"""Form used to create a new item listing."""
	institution = forms.ModelChoiceField(
		queryset=Institution.objects.all(), 
		empty_label=None,
		to_field_name='name'
	)
	category = forms.ModelChoiceField(
		label=_('Category'),
		queryset=ItemParentCategory.objects.all(), 
		empty_label=None,
		to_field_name='name'
	)
	
	# initially, it should contain the sub categories of the current(initial) selected parent category. also some user's listings might not have sub categories
	sub_category = forms.ModelChoiceField(
		label=_('Sub category'), 
		# initially set to empty queryset
		# a call will be made via ajax which will set this queryset based on the value of the parent category
		queryset=ItemCategory.objects.none(), 
		required=False
	)

	# queryset will be obtained from user's list of phone number, defined in form's __init__ method
	contact_numbers = forms.ModelMultipleChoiceField(queryset=None, required=True)
	full_name = forms.CharField(
		label=_('Full name'),
		widget=forms.TextInput(attrs={'readonly': ''}),
		required=False   
	)


	def __init__(self, *args, **kwargs):
		# Do not use kwargs.pop('user', None) due to potential security loophole (the user object must be in the form!)
		self.user = kwargs.pop('user')
		user = self.user

		super().__init__(*args, **kwargs)

		# email used for notifications concerning listing is user's email by default.
		# user may enter another email
		self.fields['contact_email'].initial = user.email
		self.fields['full_name'].initial = user.full_name
		self.fields['contact_numbers'].queryset = user.phone_numbers.all()

		# set initial value of ParentCategory queryset as first element in queryset
		# and set initial va
		# self.fields['sub_category'].initial = self.fields['category'].queryset.
		# self.fields['sub_category'].queryset = ParentCategory.objects.none()

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
				'subtitle',
				Row(
					Column('condition', css_class='form-group col-md-4 mb-0'),
					Column('condition_description', css_class='form-group col-md-8 mb-0'),
					css_class='form-row'
				),
				Formset('formset'),  # (photo formset here),
				'description',  
				Field('price', step='500')
			),
			Fieldset(_("Seller's Information"),
				'contact_email',
				'full_name',
				'contact_numbers'
				# include an "update phone number" button somewhere around here, when user clicks it, he should go to the profile update form. (directly to the phone number section will be cool)
			),
			# insert original_language as hidden field.
			Submit('submit', _('Post listing'), css_class='btn btn-primary')
		)

	class Meta:
		model = ItemListing
		exclude = ('owner', )
	

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