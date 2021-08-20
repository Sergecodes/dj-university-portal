from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from marketplace.models import Institution
from qa_site.models import Subject
from .models import PastPaper, PastPaperPhoto


class PastPaperPhotoForm(forms.ModelForm):
	file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

	class Meta:
		model = PastPaperPhoto
		fields = ('file', )


class PastPaperForm(forms.ModelForm):
	subject = forms.ModelChoiceField(
		queryset=Subject.objects.all(),
		required=False,
		help_text=_('Select the subject. Leave it empty if the subject is not in the list.')
	)
	school = forms.ModelChoiceField(
		queryset=Institution.objects.all(),
		required=False,
		help_text=_('Select the school. Allow empty if the school is not in the list.')
	)
	file = forms.FileField(
		widget=forms.FileInput(),
		required=False,
		help_text=_('<br> Pdf or .doc file of the past paper. Leave it empty if you will upload photos instead.')
	)
	# this field will be used with the PastPaperPhotoForm 
	photos = forms.FileField(
		widget=forms.FileInput(
			attrs={'multiple': True, 'accept': 'application/pdf,application/msword'}
		),
		required=False,
		help_text=_('<br> Hold down "Control", or "Command" on a Mac, to select more than one. <br> Leave it empty if you have uploaded a file instead.')
	)
	
	class Meta:
		model = PastPaper
		fields = ['school', 'subject', 'level', 'written_date', 'title', 'file', 'photos']
		widgets = {
			'title': forms.TextInput(
				attrs={'placeholder': _('Ex. Continuous Assessment(CA) Maths MCQ')}
			),
			'written_date': forms.DateInput(
				attrs={'placeholder': _('Ex. June 2020'), 'type': 'date'}
			)
		}
		help_texts = {
			'written_date': _('When this question paper was written. Just the month and year are important.'),
			'level': _('The level for which the paper was set.')
		}

	def clean(self):
		data = self.cleaned_data

		# if neither photos nor a file has been uploaded, raise error
		if not data.get('photos') and not data.get('file'):
			raise ValidationError(_("Upload either a file or some photos"))
		return self.cleaned_data
		