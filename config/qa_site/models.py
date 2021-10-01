from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template import defaultfilters as filters
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from core.constants import COMMENT_CAN_EDIT_TIME_LIMIT
from core.model_fields import TitleCaseField
from core.templatetags.app_extras import remove_tags
from flagging.models import Flag
from marketplace.models import Institution
from users.models import get_dummy_user

User = get_user_model()


class Comment(models.Model):
	flags = GenericRelation(Flag)
	posted_datetime = models.DateTimeField(auto_now_add=True)
	content = RichTextField(config_name='add_comment')
	last_modified = models.DateTimeField(auto_now=True)
	original_language = models.CharField(choices=settings.LANGUAGES, max_length=2, editable=False)
	users_mentioned = models.ManyToManyField(
		User,
		related_name='+',
		blank=True
	)
	# comments have just votes (no upvotes & downvotes)
	# vote_count = models.PositiveIntegerField(default=0)

	class Meta:
		abstract = True

	def __str__(self):
		# truncate content: https://stackoverflow.com/questions/2872512/python-truncate-a-long-string
		# see answer with textwrap.shorten ..
		return filters.truncatewords(remove_tags(self.content), 10)

	@property
	def parent_object(self):
		"""Get post under which comment belongs, used to get the url of post that contains comment."""
		# if comment is for answer
		if hasattr(self, 'answer'):
			return self.answer.question
		return self.question

	@property
	def upvote_count(self):
		return self.upvoters.count()

	@property
	def vote_count(self):
		return self.upvote_count

	@property
	def is_within_edit_timeframe(self):
		"""
		Verify if comment is within edition time_frame
		(posted_datetime is less than COMMENT_CAN_EDIT_TIME_LIMIT(5 minutes) old)
		"""
		if (timezone.now() - self.posted_datetime) > COMMENT_CAN_EDIT_TIME_LIMIT:
			return False
		return True


class SchoolQuestionComment(Comment):
	question = models.ForeignKey(
		'SchoolQuestion',
		on_delete=models.CASCADE,
		related_name='comments',
		related_query_name='comment',
	)
	poster = models.ForeignKey(
		User,
		on_delete=models.SET(get_dummy_user),
		related_name='school_question_comments',
		related_query_name='school_question_comment'
	)
	upvoters = models.ManyToManyField(
		User,
		related_name='upvoted_school_question_comments',
		related_query_name='upvoted_school_question_comment',
		blank=True
	)

	class Meta:
		verbose_name = _('School Question Comment')
		verbose_name_plural = _('School Question Comments')


class AcademicQuestionComment(Comment):
	question = models.ForeignKey(
		'AcademicQuestion',
		on_delete=models.CASCADE,
		related_name='comments',
		related_query_name='comment',
	)
	poster = models.ForeignKey(
		User,
		on_delete=models.SET(get_dummy_user),
		related_name='academic_question_comments',
		related_query_name='academic_question_comment'
	)
	upvoters = models.ManyToManyField(
		User,
		related_name='upvoted_academic_question_comments',
		related_query_name='upvoted_academic_question_comment',
		blank=True
	)

	class Meta:
		verbose_name = _('Academic Question Comment')
		verbose_name_plural = _('Academic Question Comments')


class SchoolAnswerComment(Comment):
	answer = models.ForeignKey(
		'SchoolAnswer',
		on_delete=models.CASCADE,
		related_name='comments',
		related_query_name='comment',
	)
	poster = models.ForeignKey(
		User,
		on_delete=models.SET(get_dummy_user),
		related_name='school_answer_comments',
		related_query_name='school_answer_comment'
	)
	upvoters = models.ManyToManyField(
		User,
		related_name='upvoted_school_answer_comments',
		related_query_name='upvoted_school_answer_comment',
		blank=True
	)

	class Meta:
		verbose_name = _('School Answer Comment')
		verbose_name_plural = _('School Answer Comments')


class AcademicAnswerComment(Comment):
	answer = models.ForeignKey(
		'AcademicAnswer',
		on_delete=models.CASCADE,
		related_name='comments',
		related_query_name='comment',
	)
	poster = models.ForeignKey(
		User,
		on_delete=models.SET(get_dummy_user),
		related_name='academic_answer_comments',
		related_query_name='academic_answer_comment'
	)
	upvoters = models.ManyToManyField(
		User,
		related_name='upvoted_academic_answer_comments',
		related_query_name='upvoted_academic_answer_comment',
		blank=True
	)

	class Meta:
		verbose_name = _('Academic Answer Comment')
		verbose_name_plural = _('Academic Answer Comments')


class Answer(models.Model):
	flags = GenericRelation(Flag)
	content = RichTextUploadingField(config_name='add_answer')
	posted_datetime = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)
	original_language = models.CharField(choices=settings.LANGUAGES, max_length=2, editable=False)
	# upvote_count = models.PositiveIntegerField(default=0)
	# downvote_count = models.PositiveIntegerField(default=0)

	class Meta:
		abstract = True

	def __str__(self):
		return filters.truncatewords(remove_tags(self.content), 10)

	@property
	def parent_object(self):
		return self.question

	@property 
	def upvote_count(self):
		return self.upvoters.count()

	@property 
	def downvote_count(self):
		return self.downvoters.count()

	@property
	def score(self):
		return self.upvote_count - self.downvote_count


class SchoolAnswer(Answer):
	question = models.ForeignKey(
		'SchoolQuestion',
		on_delete=models.CASCADE,
		related_name='answers',
		related_query_name='answer'
	)
	poster = models.ForeignKey(
		User,
		on_delete=models.SET(get_dummy_user),
		related_name='school_answers',
		related_query_name='school_answer'
	)
	upvoters = models.ManyToManyField(
		User,
		related_name='upvoted_school_answers',
		related_query_name='upvoted_school_answer',
		blank=True
	)
	downvoters = models.ManyToManyField(
		User,
		related_name='downvoted_school_answers',
		related_query_name='downvoted_school_answer',
		blank=True
	)

	class Meta:
		verbose_name = _('School Question Answer')
		verbose_name_plural = _('School Question Answers')


class AcademicAnswer(Answer):
	question = models.ForeignKey(
		'AcademicQuestion',
		on_delete=models.CASCADE,
		related_name='answers',
		related_query_name='answer'
	)
	poster = models.ForeignKey(
		User,
		on_delete=models.SET(get_dummy_user),
		related_name='academic_answers',
		related_query_name='academic_answer'
	)
	upvoters = models.ManyToManyField(
		User,
		related_name='upvoted_academic_answers',
		related_query_name='upvoted_academic_answer',
		blank=True
	)
	downvoters = models.ManyToManyField(
		User,
		related_name='downvoted_academic_answers',
		related_query_name='downvoted_academic_answer',
		blank=True
	)

	class Meta:
		verbose_name = _('Academic Question Answer')
		verbose_name_plural = _('Academic Question Answers')


class Question(models.Model):
	# the django-flag-app package requires that the name of this field be `flags`
	flags = GenericRelation(Flag)
	posted_datetime = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)
	original_language = models.CharField(choices=settings.LANGUAGES, max_length=2, editable=False)
	# view_count = models.PositiveIntegerField(default=0)
	# upvote_count = models.PositiveIntegerField(default=0)
	# downvote_count = models.PositiveIntegerField(default=0)

	class Meta:
		abstract = True
	
	@property
	def num_answers(self):
		return self.answers.count()

	@property 
	def upvote_count(self):
		return self.upvoters.count()

	@property 
	def downvote_count(self):
		return self.downvoters.count()

	@property
	def bookmark_count(self):
		return self.bookmarkers.count()

	@property
	def score(self):
		return self.upvote_count - self.downvote_count


class SchoolQuestionTag(models.Model):
	"""Used to define the tags for a school question."""
	# Tags include words like  registration, fees, etc...
	name = models.CharField(max_length=30, unique=True) 
	slug = models.SlugField(max_length=100) 
	datetime_added = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name.lower()

	class Meta:
		ordering = ['name']
		indexes = [
			models.Index(fields=['name'])
		]
	

class SchoolQuestion(Question):
	content = RichTextUploadingField(config_name='add_question')
	tags = models.ManyToManyField(
		SchoolQuestionTag,
		related_name='school_questions',
		related_query_name='school_question'
	)
	school = models.ForeignKey(
		Institution,
		on_delete=models.CASCADE,
		related_name='questions',
		related_query_name='question'
	)
	poster = models.ForeignKey(
		User,
		on_delete=models.SET(get_dummy_user),
		related_name='school_questions',
		related_query_name='school_question'
	)
	upvoters = models.ManyToManyField(
		User,
		related_name='upvoted_school_questions',
		related_query_name='upvoted_school_question',
		blank=True
	)
	downvoters = models.ManyToManyField(
		User,
		related_name='downvoted_school_questions',
		related_query_name='downvoted_school_question',
		blank=True
	)
	# score = models.IntegerField(editable=False)  # do this for more performance gains...
	# users following the question
	followers = models.ManyToManyField(
		User,
		related_name='following_school_questions',
		related_query_name='following_school_question',
		blank=True   # to make the field optional in admin 
	)
	# users who bookmarked(saved) the question
	bookmarkers = models.ManyToManyField(
		User,
		related_name='bookmarked_school_questions',
		related_query_name='bookmarked_school_question',
		blank=True
	)

	class Meta:
		verbose_name = _('School Question')
		verbose_name_plural = _('School Questions')
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime'])
		]

	def __str__(self):
		return filters.truncatewords(remove_tags(self.content), 10)

	def get_absolute_url(self):
		return reverse('qa_site:school-question-detail', kwargs={'pk': self.id})


class AcademicQuestion(Question):
	title = models.CharField(max_length=150)  
	# the content should be optional(like quora... perhaps some question's title may suffice..)
	content = RichTextUploadingField(config_name='add_question', blank=True)
	slug = models.SlugField(max_length=250)
	tags = TaggableManager()
	# to get tags of a given user, do something like. similar reverse relationships are also permitted.
	#	Tag.objects.filter(academicquestion__poster=user)
	#	Tag.objects.filter(academicquestion__id=a.id)  # get tags of a given question from Tag model
	# as a matter of fact, Tag has fields ('id', 'academicquestion', 'name_en', 'name_fr', 'slug', 'taggit_taggeditem_items')
	subject = models.ForeignKey(
		'Subject',
		on_delete=models.PROTECT,
		related_name='academic_questions',
		related_query_name='academic_question',
		null=True, blank=True,
		help_text=_('Allow empty if your subject is not present.')
	)
	poster = models.ForeignKey(
		User,
		on_delete=models.SET(get_dummy_user),
		related_name='academic_questions',
		related_query_name='academic_question'
	)
	upvoters = models.ManyToManyField(
		User,
		related_name='upvoted_academic_questions',
		related_query_name='upvoted_academic_question',
		blank=True
	)
	downvoters = models.ManyToManyField(
		User,
		related_name='downvoted_academic_questions',
		related_query_name='downvoted_academic_question',
		blank=True
	)
	followers = models.ManyToManyField(
		User,
		related_name='following_academic_questions',
		related_query_name='following_academic_question',
		blank=True
	)
	bookmarkers = models.ManyToManyField(
		User,
		related_name='bookmarked_academic_questions',
		related_query_name='bookmarked_academic_question',
		blank=True
	)

	class Meta:
		verbose_name = _('Academic Question')
		verbose_name_plural = _('Academic Questions')
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime'])
		]
	
	def __str__(self, *args, **kwargs):
		return self.title
		
	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.title)
		super().save(*args, **kwargs)

	def get_absolute_url(self, with_slug=True):
		if with_slug:
			return reverse('qa_site:academic-question-detail', kwargs={'pk': self.id, 'slug': self.slug})
		
		return reverse('qa_site:academic-question-detail', kwargs={'pk': self.id})


class Subject(models.Model):
	"""Subject for academic question"""
	# name = models.CharField(max_length=40, unique=True) 
	name = TitleCaseField(max_length=30, unique=True)
	slug = models.SlugField(max_length=200)
	datetime_added = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.name)
			# self.name = (self.name).title   # use python's title method (str.title)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name


# class Topic(models.Model):
# 	"""Acts as a sub category for the Subject"""
# 	name = models.CharField(max_length=50, unique=True) 
# 	subject = models.ForeignKey(
# 		Subject,
# 		on_delete=models.PROTECT,
# 		related_name='topics',
# 		related_query_name='topic'
# 	)

# 	def __str__(self):
# 		return self.name


