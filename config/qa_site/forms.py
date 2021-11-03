from taggit.forms import TagField
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.utils.translation import gettext_lazy as _

from core.constants import MAX_TAGS_PER_QUESTION
from core.models import Institution
from core.validators import validate_academic_question_tags as validate_tags
from .models import (
	AcademicAnswer, SchoolAnswer,
	AcademicAnswerComment, SchoolAnswerComment,
	AcademicQuestion, SchoolQuestion,
	AcademicQuestionComment, SchoolQuestionComment
)


class CustomTagField(TagField):
	def validate(self, value):
		# this method is created becoz apparently, when using clean_tags, 
		# the tags would have already been casted to a list and parsed by django-taggit.
		# do this here to run our own validation prior to parsing.
		super().validate(value)
		validate_tags(value)


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
	tags = CustomTagField()

	class Meta:
		model = AcademicQuestion
		fields = ['subject', 'title', 'content', 'tags', ]
		help_texts = {
			'title': _("Be specific and imagine you're asking a question to another person"),
			'tags': _(
				'Enter a space-separated list of at most {} tags. <br>'
				"Do not enter comma(\',\') or quotes(\', \")."
			).format(MAX_TAGS_PER_QUESTION)
		}
		widgets = {
			'title': forms.TextInput(attrs={
				'placeholder': _('Ex. How to transform a 3D vector to a 2D vector')
			}),
			'tags': forms.TextInput(attrs={
				'placeholder': _('Ex: tag1 tag2 tag3')
			})
		}


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


class SchoolQuestionForm(forms.ModelForm):
	school = forms.ModelChoiceField(
		queryset=Institution.objects.all(), 
		empty_label=None,
	)
	content = forms.CharField(
		widget= CKEditorUploadingWidget(
			config_name='add_school_question',
			attrs={'id': 'addQuestionWidget'}
		),
		help_text=_("Include all the information someone would need to answer your question"),
		label=_('Body'),
		required=True
	)

	class Meta:
		model = SchoolQuestion
		fields = ['school', 'content', ]


class SchoolAnswerForm(forms.ModelForm):
	content = forms.CharField(
		widget=CKEditorUploadingWidget(
			config_name='add_school_answer',
			attrs={'id': 'addAnswerWidget'}
		),
		label=_('Your Answer'),
		required=True
	)

	class Meta:
		model = SchoolAnswer
		fields = ['content', ]


class SchoolQuestionCommentForm(forms.ModelForm):
	# a ckeditor will be generated from this on the frontent
	content = forms.CharField(
		widget= CKEditorWidget(
			config_name='add_school_comment', 
			# attrs={
			# 	'placeholder': _('Use comments to ask for more information or suggest improvements.'),
			# 	'id': 'addQuestionComentArea'
			# }
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
		widget= CKEditorWidget(
			config_name='add_school_comment', 
			attrs={
				'placeholder': _('Use comments to ask for more information or suggest improvements.'),
				'class': 'js-answerComment' 
			}
		),
		help_text=_("Comments are used to ask for clarification or to point out problems in the post."),
		label='',
		required=True
	)

	class Meta:
		model = SchoolAnswerComment
		fields = ['content', ]

