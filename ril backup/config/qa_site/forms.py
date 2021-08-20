from marketplace.models import Institution
from taggit.models import Tag
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from crispy_forms.layout import (
	Layout, LayoutObject, Row, Column, Fieldset, 
	MultiField, HTML, Div, ButtonHolder,
	Button, Hidden, Reset, Submit, Field
)
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse, reverse_lazy
from django.urls.base import set_urlconf
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from core.constants import MAX_TAGS_PER_QUESTION
from .models import (
	SchoolQuestionTag, Subject, AcademicAnswer, SchoolAnswer,
	AcademicAnswerComment, SchoolAnswerComment,
	AcademicQuestion, SchoolQuestion,
	AcademicQuestionComment, SchoolQuestionComment
)


class AcademicQuestionForm(forms.ModelForm):
	content = forms.CharField(
		widget= CKEditorUploadingWidget(config_name='add_question'),
		help_text=_("Include all the information someone would need to answer your question"),
		label=_('Body'),
		required=False
	)
	subject = forms.ModelChoiceField(
		queryset=Subject.objects.all(), 
		empty_label=None,
		widget=forms.Select(attrs={})
	)
	tags = forms.ModelMultipleChoiceField(
		queryset=Tag.objects.all().order_by('name'),
		widget=forms.CheckboxSelectMultiple(),
		help_text=_("Add up to 5 tags to describe what your question is about")
	)

	class Meta:
		model = AcademicQuestion
		fields = ['subject', 'title', 'content', 'tags']
		help_texts = {
			'title': _("Be specific and imagine you're asking a question to another person")
		}

	def clean(self):
		print(self.cleaned_data)
		tags = self.cleaned_data.get('tags')
		if tags and tags.count() > MAX_TAGS_PER_QUESTION:
			raise ValidationError(_(f"Maximum {MAX_TAGS_PER_QUESTION} tags are allowed."))
		
		return self.cleaned_data


class SchoolQuestionForm(forms.ModelForm):
	school = forms.ModelChoiceField(
		queryset=Institution.objects.all(), 
		empty_label=None,
	)
	content = forms.CharField(
		widget= CKEditorUploadingWidget(config_name='add_question'),
		help_text=_("Include all the information someone would need to answer your question"),
		label=_('Body'),
		required=False
	)
	tags = forms.ModelMultipleChoiceField(
		queryset=SchoolQuestionTag.objects.all().order_by('name'),
		widget=forms.CheckboxSelectMultiple(),
		help_text=_("Add up to 5 tags to describe what your question is about")
	)

	class Meta:
		model = SchoolQuestion
		fields = ['school', 'content', 'tags']

	def clean(self):
		tags = self.cleaned_data['tags']
		if tags.count() > MAX_TAGS_PER_QUESTION:
			raise ValidationError(_(f"Maximum {MAX_TAGS_PER_QUESTION} tags are allowed."))
		
		return self.cleaned_data
		
