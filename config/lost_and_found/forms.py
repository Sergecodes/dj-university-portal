from django import forms
from django.utils.translation import gettext_lazy as _

from .models import LostItem, FoundItem


class FoundItemForm(forms.ModelForm):
	contact_numbers = forms.ModelMultipleChoiceField(
		queryset=None, 
		required=True,
		widget=forms.CheckboxSelectMultiple()
	)

	class Meta: 
		model = FoundItem
		exclude = ('tags', 'slug', 'posted_datetime', 'poster', 'original_language', 'is_outdated')
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

		self.fields['contact_email'].initial = user.email
		self.fields['contact_name'].initial = user.full_name
		self.fields['contact_numbers'].queryset = user.phone_numbers.all() 


class LostItemForm(forms.ModelForm):
	contact_numbers = forms.ModelMultipleChoiceField(
		queryset=None, 
		required=True,
		widget=forms.CheckboxSelectMultiple()
	)

	class Meta:
		model = LostItem
		exclude = ('tags', 'slug', 'posted_datetime', 'poster', 'original_language', 'is_outdated')
		widgets = {
			'item_lost': forms.TextInput(attrs={'placeholder': _('Itel smartphone')}),
			'area_lost': forms.TextInput(attrs={'placeholder': _('Infront of Amphi 250')}),
			'how_lost': forms.Textarea(attrs={
				'placeholder': _('After our class in Amphi 250, i forgot my phone on the bench near the door...'),
				'rows': '3',
			}),
			'bounty': forms.TextInput(attrs={'placeholder': _('2000Frs to the person who will return my phone to me')}),
			'item_description': forms.Textarea(attrs={'placeholder': _('The phone has a black case and a 2GB memory card is inside. ...')})
		}

	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user')
		super().__init__(*args, **kwargs)

		self.fields['contact_email'].initial = user.email
		self.fields['contact_name'].initial = user.full_name
		self.fields['contact_numbers'].queryset = user.phone_numbers.all() 
