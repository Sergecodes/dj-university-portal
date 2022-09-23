from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template import defaultfilters as filters
from django.urls import reverse
from django.utils.module_loading import import_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField
from taggit.models import TagBase, TaggedItemBase

from core.constants import (
	ACADEMIC_COMMENTS_PHOTOS_UPLOAD_DIR, 
	DISCUSS_COMMENTS_PHOTOS_UPLOAD_DIR
)
from core.models import Institution, Comment
from core.templatetags.app_extras import remove_tags
from core.utils import PhotoModelMixin
from flagging.models import Flag
from users.models import get_dummy_user
from .managers import TaggableManager

STORAGE = import_string(settings.DEFAULT_FILE_STORAGE)()
User = get_user_model()


class QaSiteComment(Comment):
	pass

	@property
	def is_reply(self):
		return not self.is_parent

	@property
	def reply_count(self):
		return self.replies.count()

	@property
	def upvote_count(self):
		return self.upvoters.count()

	@property
	def score(self):
		return self.vote_count

	class Meta:
		abstract = True


class AcademicComment(QaSiteComment):
	content = RichTextField(_('Content'), config_name='add_academic_comment')
	question = models.ForeignKey(
		'AcademicQuestion',
		on_delete=models.CASCADE,
		related_name='comments',
		related_query_name='comment',
	)
	poster = models.ForeignKey(
		User,
		on_delete=models.SET(get_dummy_user),
		related_name='academic_comments',
		related_query_name='academic_comment'
	)
	upvoters = models.ManyToManyField(
		User,
		related_name='upvoted_academic_comments',
		related_query_name='upvoted_academic_comment',
		blank=True
	)
	downvoters = models.ManyToManyField(
		User,
		related_name='downvoted_academic_comments',
		related_query_name='downvoted_academic_comment',
		blank=True
	)
	users_mentioned = models.ManyToManyField(
		User,
		related_name='academic_comments_mentioned',
		related_query_name='academic_comment_mentioned',
		blank=True
	)

	# def __str__(self):
		# 	# truncate content: https://stackoverflow.com/questions/2872512/python-truncate-a-long-string
		# 	# while you're at it, see the answer with textwrap.shorten ..
		# 	return filters.truncatewords(remove_tags(self.content), 10)

	def __str__(self):
		return self.content

	@property
	def downvote_count(self):
		return self.downvoters.count()
	
	@property
	def vote_count(self):
		return self.upvote_count - self.downvote_count

	class Meta:
		verbose_name = _('Academic Comment')
		verbose_name_plural = _('Academic Comments')


## see django-taggit docs on how to use a Custom tag
class QuestionTag(TagBase):
	# overrode name and slug coz name's maxlength is 100 and slug is 100.
	# this is bad coz if name is say 100(though almost impossible), slug will be >100 chars.
	name = models.CharField(_('Name'), unique=True, max_length=50)
	slug = models.SlugField(unique=True, max_length=100)
	datetime_added = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = _('Question Tag')
		verbose_name_plural = _('Question Tags')


class TaggedAcademicQuestion(TaggedItemBase):
	# DON'T rename this field !!
	# django-taggit says to use `content_object` as the name
	content_object = models.ForeignKey(
		'AcademicQuestion',
		on_delete=models.CASCADE
	)
	# django-taggit says to use the name `tag`
	tag = models.ForeignKey(
		QuestionTag,
		on_delete=models.CASCADE,
		related_name='academic_questions'
	)


class Question(models.Model):
	# the django-flag-app package requires that the name of this field be `flags`
	flags = GenericRelation(Flag)
	posted_datetime = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)
	original_language = models.CharField(choices=settings.LANGUAGES, max_length=2, editable=False)
	update_language = models.CharField(
		choices=settings.LANGUAGES,
		max_length=2,
		editable=False,
		blank=True
	)
	view_count = models.PositiveIntegerField(default=0)
	# upvote_count = models.PositiveIntegerField(default=0)
	# downvote_count = models.PositiveIntegerField(default=0)

	class Meta:
		abstract = True

	@property
	def answers(self):
		"""Return the parent comments as the answers to the question"""
		return self.comments.filter(parent__isnull=True)
	
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


class AcademicQuestion(Question):
	title = models.CharField(_('Title'), max_length=150, unique=True)  
	# the content should be optional(like quora... perhaps some question's title may suffice..)
	content = RichTextUploadingField(_('Content'), config_name='add_academic_question', blank=True)
	slug = models.SlugField(max_length=250)
	tags = TaggableManager(verbose_name=_('Tags'), through=TaggedAcademicQuestion, blank=True)
	subject = models.ForeignKey(
		'Subject',
		verbose_name=_('Subject'),
		on_delete=models.RESTRICT,
		related_name='academic_questions',
		related_query_name='academic_question',
		null=True, blank=True,
		help_text=_(
			'Allow this field empty if your subject is not present <br>'
			"You may add the subject's name after the question title."
		)
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
	
	def __str__(self):
		return self.title
		
	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.title)
		self.title = filters.capfirst(self.title)
		super().save(*args, **kwargs)

	def get_absolute_url(self, with_slug=True):
		if with_slug:
			return reverse('qa_site:academic-question-detail', kwargs={'pk': self.id, 'slug': self.slug})
		
		return reverse('qa_site:academic-question-detail', kwargs={'pk': self.id})


class Subject(models.Model):
	"""Subject for academic question"""
	name = models.CharField(_('Name'), max_length=50, unique=True)
	slug = models.SlugField(max_length=200)
	datetime_added = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.name)

		# title case string
		self.name = self.name.title()
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name


class DiscussComment(QaSiteComment):
	content = RichTextField(_('Content'), config_name='add_discuss_comment')
	question = models.ForeignKey(
		'DiscussQuestion',
		on_delete=models.CASCADE,
		related_name='comments',
		related_query_name='comment',
	)
	poster = models.ForeignKey(
		User,
		on_delete=models.SET(get_dummy_user),
		related_name='discuss_comments',
		related_query_name='discuss_comment'
	)
	upvoters = models.ManyToManyField(
		User,
		related_name='upvoted_discuss_comments',
		related_query_name='upvoted_discuss_comment',
		blank=True
	)
	users_mentioned = models.ManyToManyField(
		User,
		related_name='discuss_comments_mentioned',
		related_query_name='discuss_comment_mentioned',
		blank=True
	)

	def __str__(self):
		return self.content

	@property
	def vote_count(self):
		return self.upvote_count

	class Meta:
		verbose_name = _('Discuss Comment')
		verbose_name_plural = _('Discuss Comments')


class TaggedDiscussQuestion(TaggedItemBase):
	# DON'T rename this field !!
	# django-taggit says to use `content_object` as the name
	content_object = models.ForeignKey(
		'DiscussQuestion',
		on_delete=models.CASCADE
	)
	# django-taggit says to use the name `tag`
	tag = models.ForeignKey(
		QuestionTag,
		on_delete=models.CASCADE,
		related_name='discuss_questions'
	)


class DiscussQuestion(Question):
	# no title for discussion question...
	# discussion questions are generally short and straight forward,
	# so instead of creating a title field, 
	# in which case some users will optionally and rarely fill the content field,
	# just use a one-size-fits-all content field.
	content = RichTextUploadingField(config_name='add_discuss_question')
	# If question concerns a school
	school = models.ForeignKey(
		Institution,
		on_delete=models.CASCADE,
		related_name='questions',
		related_query_name='question',
		blank=True, null=True
	)
	tags = TaggableManager(verbose_name=_('Tags'), through=TaggedDiscussQuestion, blank=True)
	poster = models.ForeignKey(
		User,
		on_delete=models.SET(get_dummy_user),
		related_name='discuss_questions',
		related_query_name='discuss_question'
	)
	upvoters = models.ManyToManyField(
		User,
		related_name='upvoted_discuss_questions',
		related_query_name='upvoted_discuss_question',
		blank=True
	)
	downvoters = models.ManyToManyField(
		User,
		related_name='downvoted_discuss_questions',
		related_query_name='downvoted_discuss_question',
		blank=True
	)
	followers = models.ManyToManyField(
		User,
		related_name='following_discuss_questions',
		related_query_name='following_discuss_question',
		blank=True   # to make the field optional in admin 
	)
	bookmarkers = models.ManyToManyField(
		User,
		related_name='bookmarked_discuss_questions',
		related_query_name='bookmarked_discuss_question',
		blank=True
	)

	class Meta:
		verbose_name = _('Discussion Question')
		verbose_name_plural = _('Discussion Questions')
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime'])
		]

	def __str__(self):
		return filters.truncatewords(remove_tags(self.content), 10)

	def save(self, *args, **kwargs):
		self.content = filters.capfirst(self.content)
		super().save(*args, **kwargs)

	def get_absolute_url(self):
		return reverse('qa_site:discuss-question-detail', kwargs={'pk': self.id})


class DiscussCommentPhoto(models.Model, PhotoModelMixin):
	file = ThumbnailerImageField(
		thumbnail_storage=STORAGE, 
		upload_to=DISCUSS_COMMENTS_PHOTOS_UPLOAD_DIR
	)
	upload_datetime = models.DateTimeField(auto_now_add=True)
	comment = models.ForeignKey(
		DiscussComment,
		on_delete=models.CASCADE,
		related_name='photos',
		related_query_name='photo',
		null=True, blank=True  
	)

	def __str__(self):
		return self.actual_filename

	class Meta:
		verbose_name = 'Discussion Comment Photo'
		verbose_name_plural = 'Discussion Comments Photos'


class AcademicCommentPhoto(models.Model, PhotoModelMixin):
	file = ThumbnailerImageField(
		thumbnail_storage=STORAGE, 
		upload_to=ACADEMIC_COMMENTS_PHOTOS_UPLOAD_DIR
	)
	upload_datetime = models.DateTimeField(auto_now_add=True)
	comment = models.ForeignKey(
		AcademicComment,
		on_delete=models.CASCADE,
		related_name='photos',
		related_query_name='photo',
		null=True, blank=True  
	)

	def __str__(self):
		return self.actual_filename

	class Meta:
		verbose_name = 'Academic Comment Photo'
		verbose_name_plural = 'Academic Comments Photos'


