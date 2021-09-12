from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.forms import PhotoFormLayout
from marketplace.models import Institution
from qa_site.models import Subject
from .models import PastPaper, PastPaperPhoto, Comment


class PastPaperPhotoForm(forms.ModelForm):
	file = forms.FileField(
		widget=forms.ClearableFileInput(attrs={'multiple': True}), 
		help_text=_('These photos will be converted to a PDF file.')
	)

	class Meta:
		model = PastPaperPhoto
		fields = ('file', )


class CommentForm(forms.ModelForm):

	class Meta:
		model = Comment
		fields = ('content', )
		labels = {
			'content': _('Comment')
		}
		widgets = {
			'content': forms.Textarea(attrs={
				'placeholder': _('Enter your comment...'),
				'rows': '2',
			})
		}


class PastPaperForm(forms.ModelForm):
	level = forms.ChoiceField(
		choices=PastPaper.LEVELS,
		initial=PastPaper.ORDINARY_LEVEL,
		widget=forms.Select()
	)
	file = forms.FileField(
		widget=forms.FileInput(
			attrs={'accept': 'application/pdf'},
		),
		required=False,
		help_text=_('Pdf file of the past paper. Leave it empty if you will upload photos instead.')
	)
	# this field will be used with the PastPaperPhotoForm 
	# photos = forms.ImageField(
	# 	widget=forms.FileInput(attrs={'multiple': True}),
	# 	required=False,
	# 	help_text=_('Hold down "Control", or "Command" on a Mac, to select more than one. <br> Leave it empty if you have uploaded a file instead.')
	# )
	
	class Meta:
		model = PastPaper
		fields = ['school', 'type', 'level', 'subject', 'written_date', 'title', 'file']
		widgets = {
			'title': forms.TextInput(
				attrs={'placeholder': _('Ex. 3rd sequence exam Maths Form 5 MCQ')}
			),
			'written_date': forms.DateInput(
				attrs={'placeholder': _('Ex. June 2020'), 'type': 'date'}
			)
		}
		help_texts = {
			'title': _('Please include the class and subject name in the title.'),
			'written_date': _('Optional. When this question paper was written. <br> Just the month and year will suffice, you can enter any day.'),
			'level': _('The level for which the paper was set.'),
			'school': _('Select the school. Allow empty if your school is not in the list.'),
			'subject': _('Select the subject. Leave it empty if the subject is not in the list.'),
		}

	def __init__(self, *args, **kwargs):
		initial_photos = kwargs.pop('initial_photos', [])
		super().__init__(*args, **kwargs)

		# self.fields['subject'].empty_label = None

		self.helper = FormHelper()
		self.helper.layout = Layout(
			'school', 
			'type',
			'level',
			'subject', 
			'written_date',
			'title',
			'file',
			PhotoFormLayout(extra_context={
				'form_for': 'past_paper', 
				'upload_help_text': _('Upload photo(s) if you have not uploaded any file.'),
				'initial_photos': initial_photos
			}),  
			Submit('submit', _('Upload'), css_class='btn-success'),
		)

	# def clean(self):
	# 	data = self.cleaned_data

	# 	# if neither photos nor a file has been uploaded, raise error
	# 	if not data.get('photos') and not data.get('file'):
	# 		self.add_error(None, ValidationError(_("Upload either a file or photo(s), but not both.")))

	# 	return data
		