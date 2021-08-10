from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from datetime import timedelta
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
# from django.core.validators import validate_email
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.model_fields import LowerCaseEmailField, TitleCaseField
from marketplace.models import Institution
from hitcount.models import HitCountMixin

User = settings.AUTH_USER_MODEL

# comment, upvote, downvote
class Comment(models.Model):
	posted_datetime = models.DateTimeField(auto_now_add=True)
	body = RichTextField()

	class Meta:
		abstract = True


class QuestionComment(models.Model):
	question = models.ForeignKey(
		'Question',
		on_delete=models.CASCADE,
		related_name='comments',
		related_query_name='comment',
	)
	poster = models.ForeignKey(
		'Profile',
		on_delete=models.SET(get_sentinel_profile),
		related_name='comments',
		related_query_name='comment'
	)
	score = models.PositiveIntegerField(default=0)


class Answer(models.Model):
	body = RichTextUploadingField()
	posted_datetime = models.DateTimeField(auto_now_add=True)
	question = models.ForeignKey(
		'Question',
		related_name='answers',
		related_query_name='answer'
	)


class Question(models.Model):
	posted_datetime = models.DateTimeField(auto_now_add=True)
	followers = models.ManyToManyField(
		User,
		related_name='questions_following',
		related_query_name='question'
	)
	
	class Meta:
		abstract = True


class InstitutionQuestion(Question):
	institution = models.ForeignKey(
		Institution,
		on_delete=models.CASCADE,
		related_name='questions',
		related_query_name='question'
	)
	poster = models.ForeignKey(
		User,
		related_name='school_questions',
		related_query_name='question'
	)


class AcademicQuestion(Question):
	poster = models.ForeignKey(
		User,
		related_name='academic_questions',
		related_query_name='question'
	)


class Subject(models.Model):
	"""Subject for academic question"""
	name = models.CharField(max_length=40, unique=True)


class Topic(models.Model):
	"""Acts as a sub category for the Subject"""
	name = models.CharField(max_length=50, unique=True) 
	subject = models.ForeignKey(
		Subject,
		on_delete=models.PROTECT,
		related_name='topics',
		related_query_name='topic'
	)
