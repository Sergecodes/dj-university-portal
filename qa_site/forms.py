from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.constants import MAX_TAGS_PER_QUESTION, MAX_TAGS_PER_DISCUSSION
from core.validators import validate_question_tags as validate_tags
from .models import (
	AcademicAnswer, AcademicAnswerComment, AcademicQuestion, 
	DiscussQuestion, AcademicQuestionComment, DiscussComment
)


class AcademicQuestionForm(forms.ModelForm):
	# use ckeditor widget due to server upload image functionality. 
	# server upload doesn't work with dynamically created instances via js.
	content = forms.CharField(
		widget=CKEditorUploadingWidget(
			config_name='add_academic_question',
			# id is required so that ck-editor instances be unique
			attrs={'id': 'addQuestionWidget'}
		),
		help_text=_("Include all the information someone would need to answer your question"),
		label=_('Body'),
		required=False
	)

	class Meta:
		model = AcademicQuestion
		fields = ['subject', 'title', 'content', 'tags', ]
		help_texts = {
			'title': _("Be specific and imagine you're asking a question to another person"),
			'tags': _(
				'Enter at most {} tags. '
				"Only alphanumeric characters and hyphens are supported."
			).format(MAX_TAGS_PER_QUESTION)
		}
		widgets = {
			'title': forms.TextInput(attrs={
				'placeholder': _('Ex. How to transform a 3D vector to a 2D vector')
			}),
		}

	def clean_tags(self):
		tags = self.cleaned_data['tags']

		try:
			validate_tags(tags, MAX_TAGS_PER_QUESTION)
		except ValidationError as err:
			self.add_error('tags', err)
		else:
			return tags
		

class AcademicAnswerForm(forms.ModelForm):
	content = forms.CharField(
		# use ckeditor widget due to server upload image functionality. 
		# server upload doesn't work with dynamically created instances via js.
		widget=CKEditorUploadingWidget(
			config_name='add_academic_answer',
			attrs={'id': 'addAnswerWidget'}
		),
		label=_('Your Answer'),
		required=True
	)

	class Meta:
		model = AcademicAnswer
		fields = ['content', ]


class AcademicQuestionCommentForm(forms.ModelForm):
	content = forms.CharField(
		widget= CKEditorWidget(
			config_name='add_academic_comment', 
			# attrs={
			# 	'placeholder': _('Use comments to ask for more information or suggest improvements.'),
			# 	# # set unique id for ckeditor widget 
			# 	# # this id ain't even required.
			# 	# 'id': 'addQuestionCommentArea'		
			# }
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
		widget= CKEditorWidget(
			config_name='add_academic_comment', 
			attrs={
				'placeholder': _('Use comments to ask for more information or suggest improvements.'),
				# use this class
				'class': 'js-answerComment'
			}
		),
		help_text=_("Comments are used to ask for clarification or to point out problems in the post."),
		label='',
		required=True
	)

	class Meta:
		model = AcademicAnswerComment
		fields = ['content', ]


class DiscussQuestionForm(forms.ModelForm):
	content = forms.CharField(
		widget=CKEditorUploadingWidget(
			config_name='add_discuss_question',
			attrs={'id': 'addQuestionWidget'}
		),
		help_text=_("Include all the information someone would need to answer your question"),
		label=_('Question'),
		required=True
	)

	class Meta:
		model = DiscussQuestion
		fields = ['school', 'content', 'tags', ]
		help_texts={
			'school': _("Allow this field empty if the question does not concern a particular school"),
			'tags': _(
				'Enter at most {} tags. '
				"Only alphanumeric characters and hyphens are supported."
			).format(MAX_TAGS_PER_DISCUSSION)
		}

	def clean_tags(self):
		# tags is an array of strings
		tags = self.cleaned_data['tags']

		try:
			validate_tags(tags, MAX_TAGS_PER_DISCUSSION)
		except ValidationError as err:
			self.add_error('tags', err)
		else:
			return tags


class DiscussCommentForm(forms.ModelForm):
	# a ckeditor will be generated from this on the frontent
	content = forms.CharField(
		widget= CKEditorWidget(
			config_name='add_discuss_comment',
		),
		help_text=_("Comments are used to ask for clarification or to point out problems in the post."),
		label='',
		required=True
	)

	class Meta:
		model = DiscussComment
		fields = ['content', 'parent', ]

