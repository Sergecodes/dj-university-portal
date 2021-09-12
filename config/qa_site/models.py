from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from core.model_fields import TitleCaseField
from marketplace.models import Institution
from users.models import get_dummy_user

User = get_user_model()


class Comment(models.Model):
	posted_datetime = models.DateTimeField(auto_now_add=True)
	content = RichTextField()
	last_modified = models.DateTimeField(auto_now=True)
	# comments have just votes (no upvotes & downvotes)
	# vote_count = models.PositiveIntegerField(default=0)

	class Meta:
		abstract = True

	def __str__(self):
		# truncate content: https://stackoverflow.com/questions/2872512/python-truncate-a-long-string
		# see answer with textwrap.shorten ..
		return self.content
	
	@property
	def vote_count(self):
		return self.upvoters.count()


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
	content = RichTextUploadingField()
	posted_datetime = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)
	# upvote_count = models.PositiveIntegerField(default=0)
	# downvote_count = models.PositiveIntegerField(default=0)

	class Meta:
		abstract = True

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
	posted_datetime = models.DateTimeField(auto_now_add=True)
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
	def score(self):
		return self.upvote_count - self.downvote_count


class SchoolQuestionTag(models.Model):
	"""Used to define the tags for a school question."""
	# Tags include words like  registration, fees, etc...
	name = models.CharField(max_length=30, unique=True) 
	slug = models.SlugField(max_length=100) 
	datetime_added = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.name)
		return super().save(*args, **kwargs)

	def __str__(self):
		return self.name.lower()

	class Meta:
		ordering = ['name']
		indexes = [
			models.Index(fields=['name'])
		]
	

class SchoolQuestion(Question):
	content = RichTextUploadingField()
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
		return self.content

	def get_absolute_url(self):
		return reverse('qa_site:school-question-detail', kwargs={'pk': self.id})


class AcademicQuestion(Question):
	title = models.CharField(max_length=150)  
	# the content should be optional(like quora... perhaps some question's title may suffice..)
	content = RichTextUploadingField(blank=True)
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
		related_query_name='academic_question'
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

	def get_absolute_url(self):
		return reverse('qa_site:academic-question-detail', kwargs={'pk': self.id, 'slug': self.slug})


class Subject(models.Model):
	"""Subject for academic question"""
	# name = models.CharField(max_length=40, unique=True) 
	name = TitleCaseField(max_length=30, unique=True)
	slug = models.SlugField(max_length=200)
	datetime_added = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.name)
			# self.name = (self.name).title   # use python's title method (str.title)
		return super().save(*args, **kwargs)

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


