from django import forms

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
		required=False
	)
	school = forms.ModelChoiceField(
		queryset=Institution.objects.all(),
		required=False
	)
	# this field will be used with the PastPaperPhotoForm 
	photos = forms.FileField(
		widget=forms.ClearableFileInput(attrs={'multiple': True}),
		required=False
	)
	
	class Meta:
		model = PastPaper
		fields = ['school', 'subject', 'title', 'file', 'photos']

		