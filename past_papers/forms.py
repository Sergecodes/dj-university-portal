from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django import forms
from django.utils.translation import gettext_lazy as _
# from easy_thumbnails.widgets import ImageClearableFileInput

from core.forms import PhotoFormLayout
from core.utils import PhotoUploadMixin, get_country
from .models import PastPaper, PastPaperPhoto, Comment


class PastPaperPhotoForm(forms.ModelForm, PhotoUploadMixin):
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
	
	class Meta:
		model = PastPaper
		fields = [
			'country', 'type', 'level', 'subject', 
			'written_date', 'title', 'file', 
		]
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
			'written_date': _(
				'Optional. When this question paper was written. <br> '
				'Just the month and year will suffice, you can enter any day.'
			),
			'level': _('The level for which the paper was set.'),
			'subject': _('Select the subject. Allow empty if the subject is not in the list.'),
		}

	def __init__(self, *args, **kwargs):
		initial_photos = kwargs.pop('initial_photos', [])
		country_or_code = kwargs.pop('country_or_code')
		super().__init__(*args, **kwargs)

		country = get_country(country_or_code)
		self.fields['country'].initial = country.pk
		self.fields['country'].empty_label = None

		self.helper = FormHelper()
		self.helper.layout = Layout(
			Row(
				Column('country', css_class='form-group col-md-6'),
				Column('type', css_class='form-group col-md-6'),
				Column('level', css_class='form-group col-md-6'),
				Column('subject', css_class='form-group col-md-6'),
				css_class='form-row'
			),
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
		