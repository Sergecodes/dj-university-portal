from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms import PhotoFormLayout
from .models import LostItem, LostItemPhoto, FoundItem


class LostItemPhotoForm(forms.ModelForm):
	class Meta:
		model = LostItemPhoto
		fields = ('file', )


class FoundItemForm(forms.ModelForm):
	contact_numbers = forms.ModelMultipleChoiceField(
		queryset=None, 
		required=True,
		widget=forms.CheckboxSelectMultiple()
	)

	class Meta: 
		model = FoundItem
		exclude = ('slug', 'posted_datetime', 'poster', 'original_language', 'is_outdated')
		widgets = {
			'item_found': forms.TextInput(attrs={'placeholder': _('Green backpack')}),
			'area_found': forms.TextInput(attrs={'placeholder': _('Infront of Amphi 250')}),
			'how_found': forms.Textarea(attrs={
				'placeholder': _('I was walking near Amphi 250 and found the green backpack near the door.'),
				'rows': '3',
			}),
		}

	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user')
		super().__init__(*args, **kwargs)

		# email used for notifications concerning listing is user's email by default.
		# user may enter another email
		self.fields['contact_email'].initial = user.email
		self.fields['contact_name'].initial = user.full_name
		self.fields['contact_numbers'].queryset = user.phone_numbers.all()
		self.fields['school'].empty_label = None

		self.helper = FormHelper()
		self.helper.layout = Layout(
			Fieldset(_('Found Item Information'),
				'school',
				'item_found',
				'area_found',
				'how_found'
			),
			Fieldset(_("Poster's Information"),
				'contact_email',
				'contact_name',
				'contact_numbers'
			),
			HTML(" \
				<button \
					class='btn btn-outline text-primary d-inline-block mb-4 pt-0' \
					type='button' \
					data-bs-toggle='modal' \
					data-bs-target='#leavePageModal' \
				>" +  str(_('Edit phone numbers')) + 
				'<i class="fas fa-external-link-alt ms-2" aria-hidden="true"></i>' + 
				"</button>"
			),
			Submit('submit', _('Publish item'), css_class='d-block'),
		)


class LostItemForm(forms.ModelForm):
	contact_numbers = forms.ModelMultipleChoiceField(
		queryset=None, 
		required=True,
		widget=forms.CheckboxSelectMultiple()
	)

	class Meta:
		model = LostItem
		exclude = ('slug', 'posted_datetime', 'poster', 'original_language', 'is_outdated')
		widgets = {
			'item_lost': forms.TextInput(attrs={'placeholder': _('Itel smartphone')}),
			'area_lost': forms.TextInput(attrs={'placeholder': _('Infront of Amphi 250')}),
			'how_lost': forms.Textarea(attrs={
				'placeholder': _('After our class in Amphi 250, i forgot my phone on the bench near the door then...'),
				'rows': '3',
			}),
			'bounty': forms.TextInput(attrs={'placeholder': _('2000F to the person who will return my phone to me')}),
			'item_description': forms.Textarea(attrs={'placeholder': _('The phone has a black case and a 2GB memory card is inside ...'), 'rows': '3'})
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
			Fieldset(_('Lost Item Information'),
				'school',
				'item_lost',
				'item_description',
				PhotoFormLayout(extra_context={
					'form_for': 'lost_item', 
					'upload_help_text': _("Upload maximum 3 photos of the lost item. Allow this empty if you do not have any photos."),
					'photos': initial_photos
				}),  
				'area_lost',
				'how_lost'
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
				>" +  str(_('Edit phone numbers')) + 
				'<i class="fas fa-external-link-alt ms-2" aria-hidden="true"></i>' + 
				"</button>"
			),
			Submit('submit', _('Publish item'), css_class='d-block'),
		)


