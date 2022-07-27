from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import FileExtensionValidator
from django.db import models
from django.template import defaultfilters as filters
from django.urls import reverse
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField

from core.constants import (
	PAST_PAPERS_UPLOAD_DIR, PAST_PAPERS_PHOTOS_UPLOAD_DIR,
	PAST_PAPER_CAN_DELETE_TIME_LIMIT, 
	PAST_PAPER_COMMENT_CAN_DELETE_TIME_LIMIT,
	PAST_PAPER_COMMENT_CAN_EDIT_TIME_LIMIT, 
)
from core.models import Country
from core.fields import DynamicStorageFileField
from core.utils import PhotoModelMixin
from flagging.models import Flag
from qa_site.models import Subject
from users.models import get_dummy_user

STORAGE = import_string(settings.DEFAULT_FILE_STORAGE)()
User = get_user_model()
 
 
class PastPaperPhoto(models.Model, PhotoModelMixin):
	"""
	These photos should be periodically removed from storage, since after upload they are practically useless since they are used solely to generate the pdf file containing these photos...
	"""
	file = ThumbnailerImageField(
		thumbnail_storage=STORAGE, 
		upload_to=PAST_PAPERS_PHOTOS_UPLOAD_DIR
	)
	upload_datetime = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.actual_filename


class Comment(models.Model):
	flags = GenericRelation(Flag)
	content = models.TextField(_('Content'))
	poster = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='past_paper_comments',
		related_query_name='past_paper_comment'
	)
	past_paper = models.ForeignKey(
		'PastPaper',
		on_delete=models.CASCADE,
		related_name='comments',
		related_query_name='comment'
	)
	original_language = models.CharField(choices=settings.LANGUAGES, max_length=2, editable=False)
	update_language = models.CharField(
		choices=settings.LANGUAGES,
		max_length=2,
		editable=False,
		blank=True
	)
	posted_datetime = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime'])
		]

	def __str__(self):
		return filters.truncatewords(self.content, 10)

	@property
	def parent_object(self):
		return self.past_paper

	@property
	def is_within_edit_timeframe(self):
		"""
		Verify if past paper comment is within edition time_frame
		"""
		if (timezone.now() - self.posted_datetime) > PAST_PAPER_COMMENT_CAN_EDIT_TIME_LIMIT:
			return False
		return True

	@property
	def is_within_delete_timeframe(self):
		"""
		Verify if past paper comment is within deletion time_frame
		"""
		if (timezone.now() - self.posted_datetime) > PAST_PAPER_COMMENT_CAN_DELETE_TIME_LIMIT:
			return False
		return True


class PastPaper(models.Model):
	"""Official past papers and papers for revision."""
	ORDINARY_LEVEL = 'O'
	ADVANCED_LEVEL = 'A'
	BEPC = 'BEPC'
	PROBATOIRE = 'PROB'
	BACCALAUREAT = 'BAC'
	BACHELORS = 'BACH'
	BTS = 'BTS'
	LICENCE = 'LIC'
	MASTERS = 'MS' 
	DOCTORATE = 'PhD'

	# use lists(mutable) instead of tuples.
	# so as to enable copying it withoud needing to cast it.
	# eg. see SocialProfileForm init method
	# TODO add others
	LEVELS = [
		(ORDINARY_LEVEL, 'Ordinary Level'),
		(ADVANCED_LEVEL, 'Advanced Level'),
		(BEPC, 'BEPC'), 
		(PROBATOIRE, 'Probatoire'), 
		(BACCALAUREAT, 'Baccalaureat'), 
		(BACHELORS, "HND/Bachelor's"), 
		(BTS, 'BTS'),
		(LICENCE, 'Licence'),
		(MASTERS, _("Master's")),
		(DOCTORATE, _('Doctorate'))
	]

	COMMERCIAL = 'COMM'
	GENERAL = 'GEN'
	TECHNICAL = 'TECH'

	# TODO add others
	TYPES = (
		(COMMERCIAL, _('Commercial')),
		(GENERAL, _('General')),
		(TECHNICAL, _('Technical'))
	)
	
	level = models.CharField(_('Level'), max_length=5, choices=LEVELS)
	type = models.CharField(_('Speciality'), max_length=5, choices=TYPES, default='GEN')
	title = models.CharField(_('Title'), max_length=100, unique=True)
	slug = models.SlugField(max_length=250)
	flags = GenericRelation(Flag)
	# actual file corresponding to past paper
	file = DynamicStorageFileField(
		upload_to=PAST_PAPERS_UPLOAD_DIR, 
		validators=[FileExtensionValidator(['pdf'])],
		blank=True
	)
	poster = models.ForeignKey(
		User,
		on_delete=models.SET(get_dummy_user),
		related_name='past_papers',
		related_query_name='past_paper'
	) 
	bookmarkers = models.ManyToManyField(
		User,
		related_name='bookmarked_past_papers',
		related_query_name='bookmarked_past_paper',
		blank=True
	)
	country = models.ForeignKey(
		Country,
		verbose_name=_('Country'),
		on_delete=models.RESTRICT,
		related_name='past_papers',
		related_query_name='past_paper',
	)
	subject = models.ForeignKey(
		Subject,
		verbose_name=_('Subject'),
		on_delete=models.RESTRICT,
		related_name='past_papers',
		related_query_name='past_paper',
		blank=True, null=True
	)
	posted_datetime = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)
	# when the past paper was written..
	# those with null=True will be considered as revision papers..
	written_date = models.DateField(_('Written date'), null=True, blank=True) 
	# language not original_language. this model is not translatable. 
	language = models.CharField(choices=settings.LANGUAGES, default='en', max_length=2)
	view_count = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = filters.slugify(self.title)
		self.title = filters.capfirst(self.title)
		super().save(*args, **kwargs)

	def get_absolute_url(self, with_slug=True):
		if with_slug:
			return reverse('past_papers:past-paper-detail', kwargs={'pk': self.id, 'slug': self.slug})
		return reverse('past_papers:past-paper-detail', kwargs={'pk': self.id})

	@property
	def bookmark_count(self):
		return self.bookmarkers.count()

	@property
	def num_comments(self):
		return self.comments.count()

	@property
	def is_within_delete_timeframe(self):
		"""
		Verify if past paper is within deletion time_frame
		"""
		if (timezone.now() - self.posted_datetime) > PAST_PAPER_CAN_DELETE_TIME_LIMIT:
			return False
		return True

	@property
	def actual_filename(self):
		"""
		Get name of file with extension (not relative path from MEDIA_URL).
		If files have the same name, Django automatically appends a unique string to each file before storing.
		This property(function) returns the name of a file (on disk) with its extension.
		Ex. `Screenshot_from_2020_hGETyTo.png` or `Screenshot_from_2020.png`

		This differs from self.file.name in that the latter also includes the upload_to directory of the file.
		"""
		import os

		return os.path.basename(self.file.name)


	class Meta:
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime'])
		]

