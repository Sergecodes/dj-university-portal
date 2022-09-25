# from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image, UnidentifiedImageError

from core.constants import MAX_TAGS_PER_QUESTION, MAX_TAGS_PER_DISCUSSION, VALID_IMAGE_FILETYPES
from core.validators import validate_question_tags as validate_tags
from .models import (
	AcademicQuestion, DiscussQuestion, AcademicComment, DiscussComment,
	AcademicCommentPhoto, DiscussCommentPhoto
)


class AcademicCommentPhotoForm(forms.ModelForm):
	attachments = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

	class Meta:
		model = AcademicCommentPhoto
		fields = ('attachments', )

	def clean_attachments(self):
		files = self.files.getlist('attachments')
		try:
			for file in files:
				format = Image.open(file).format
				file.seek(0)
				
				if format in VALID_IMAGE_FILETYPES:
					continue
				else:	
					self.add_error('attachments', _('Invalid file format, only JPEG/PNG are permitted'))
					break
		except UnidentifiedImageError:
			self.add_error('attachments', _('Invalid file format, only JPEG/PNG are permitted'))

		return files


class DiscussCommentPhotoForm(forms.ModelForm):
	attachments = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

	class Meta:
		model = DiscussCommentPhoto
		fields = ('attachments', )

	def clean_attachments(self):
		files = self.files.getlist('attachments')
		try:
			for file in files:
				format = Image.open(file).format
				file.seek(0)
				
				if format in VALID_IMAGE_FILETYPES:
					continue
				else:	
					self.add_error('attachments', _('Invalid file format, only JPEG/PNG are permitted'))
					break
		except UnidentifiedImageError:
			self.add_error('attachments', _('Invalid file format, only JPEG/PNG are permitted'))

		return files


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
		

class AcademicCommentForm(forms.ModelForm):
	pass
	# a ckeditor will be generated from this on the frontend.
	#
	# content = forms.CharField(
	# 	widget= CKEditorWidget(
	# 		config_name='add_academic_comment',
	# 	),
	# 	help_text=_("Comments are used to ask for clarification or to point out problems in the post."),
	# 	label='',
	# 	required=True
	# )

	class Meta:
		model = AcademicComment
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
	pass
	# a ckeditor will be generated from this on the frontend.
	#
	# content = forms.CharField(
	# 	widget= CKEditorWidget(
	# 		config_name='add_discuss_comment',
	# 	),
	# 	help_text=_("Comments are used to ask for clarification or to point out problems in the post."),
	# 	label='',
	# 	required=True
	# )

	class Meta:
		model = DiscussComment
		fields = ['content', ]


