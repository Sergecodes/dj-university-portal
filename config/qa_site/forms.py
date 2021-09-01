import uuid
from taggit.models import Tag
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.constants import MAX_TAGS_PER_QUESTION
from marketplace.models import Institution
from .models import (
	SchoolQuestionTag, Subject, AcademicAnswer, SchoolAnswer,
	AcademicAnswerComment, SchoolAnswerComment,
	AcademicQuestion, SchoolQuestion,
	AcademicQuestionComment, SchoolQuestionComment
)


class AcademicQuestionForm(forms.ModelForm):
	content = forms.CharField(
		widget=CKEditorUploadingWidget(config_name='add_question'),
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
		widgets = {
			'title': forms.TextInput(attrs={
				'placeholder': _('Ex. How to transform a 3D vector to a 2D vector')
			})
		}

	def clean(self):
		tags = self.cleaned_data.get('tags')
		if tags and tags.count() > MAX_TAGS_PER_QUESTION:
			raise ValidationError(_(f"Maximum {MAX_TAGS_PER_QUESTION} tags are allowed."))
		
		return self.cleaned_data


class AcademicAnswerForm(forms.ModelForm):
	content = forms.CharField(
		# use ckeditor widget due to server upload image functionality. it doesn't work with dynamically created instances via js.
		widget=CKEditorUploadingWidget(config_name='add_answer'),
		label=_('Your Answer'),
		required=True
	)

	class Meta:
		model = AcademicAnswer
		fields = ['content', ]


class AcademicQuestionCommentForm(forms.ModelForm):
	content = forms.CharField(
		# widget= CKEditorWidget(
		# 	config_name='add_comment', 
		# 	attrs={'placeholder': _('Use comments to ask for more information or suggest improvements.')}
		# ),
		widget= forms.Textarea(
			attrs={
				'placeholder': _('Use comments to ask for more information or suggest improvements.'),
				'id': 'addQuestionCommentArea',
				# 'rows': '3',
			}
		),
		help_text=_("Comments are used to ask for clarification or to point out problems in the post."),
		label='',
		required=True
	)

	class Meta:
		model = AcademicQuestionComment
		fields = ['content', ]


class AcademicAnswerCommentForm(forms.ModelForm):
	content = forms.CharField(
		# widget= CKEditorWidget(
		# 	config_name='add_comment', 
		# 	attrs={'placeholder': _('Use comments to ask for more information or suggest improvements.')}
		# ),
		widget= forms.Textarea(
			attrs={
				'placeholder': _('Use comments to ask for more information or suggest improvements.'),
				# there may be many answers on a page, hence many answer forms. so generate unique id for ckeditor widget of each form
				'id': str(uuid.uuid4()).split('-')[0]
			}
		),
		help_text=_("Comments are used to ask for clarification or to point out problems in the post."),
		label='',
		required=True
	)

	class Meta:
		model = AcademicAnswerComment
		fields = ['content', ]


class SchoolQuestionForm(forms.ModelForm):
	school = forms.ModelChoiceField(
		queryset=Institution.objects.all(), 
		empty_label=None,
	)
	content = forms.CharField(
		widget= CKEditorUploadingWidget(config_name='add_question'),
		help_text=_("Include all the information someone would need to answer your question"),
		label=_('Body'),
		required=True
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
		tags = self.cleaned_data.get('tags')
		# if not tags:
		# 	raise ValidationError(_('Select at least one tag'))

		if tags and tags.count() > MAX_TAGS_PER_QUESTION:
			self.add_error('tags', ValidationError(_(f"Maximum {MAX_TAGS_PER_QUESTION} tags are allowed.")))
		
		return self.cleaned_data
		

class SchoolAnswerForm(forms.ModelForm):
	content = forms.CharField(
		# use ckeditor widget due to server upload image functionality. it doesn't work with dynamically created instances via js.
		widget=CKEditorUploadingWidget(config_name='add_answer'),
		label=_('Your Answer'),
		required=True
	)

	class Meta:
		model = SchoolAnswer
		fields = ['content', ]


class SchoolQuestionCommentForm(forms.ModelForm):
	# a ckeditor will be generated from this on the frontent
	content = forms.CharField(
		widget= forms.Textarea(
			attrs={
				'placeholder': _('Use comments to ask for more information or suggest improvements.'),
				'id': 'addQuestionCommentArea',
				# 'rows': '3',
			}
		),
		help_text=_("Comments are used to ask for clarification or to point out problems in the post."),
		label='',
		required=True
	)

	class Meta:
		model = SchoolQuestionComment
		fields = ['content', ]


class SchoolAnswerCommentForm(forms.ModelForm):
	content = forms.CharField(
		widget= forms.Textarea(
			attrs={
				'placeholder': _('Use comments to ask for more information or suggest improvements.'),
				# there may be many answers on a page, hence many answer forms. so generate unique id for ckeditor widget of each form
				'id': str(uuid.uuid4()).split('-')[0]
			}
		),
		help_text=_("Comments are used to ask for clarification or to point out problems in the post."),
		label='',
		required=True
	)

	class Meta:
		model = SchoolAnswerComment
		fields = ['content', ]

