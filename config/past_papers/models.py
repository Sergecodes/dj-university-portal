from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from flagging.models import Flag

from core.constants import PAST_PAPERS_UPLOAD_DIR, PAST_PAPERS_PHOTOS_UPLOAD_DIR
from marketplace.models import Institution
from qa_site.models import Subject
from users.models import get_dummy_user

User = get_user_model()
 
 
class PastPaperPhoto(models.Model):
	"""
	These photos should be periodically removed from storage, since after upload they are practically useless since they are used solely to generate the pdf file containing these photos...
	"""
	file = models.ImageField(upload_to=PAST_PAPERS_PHOTOS_UPLOAD_DIR)
	upload_datetime = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.actual_filename

	@cached_property
	def actual_filename(self):
		"""
		Get file name of file with extension (not relative path from MEDIA_URL).
		If files have the same name, Django automatically appends a unique string to each file before storing.
		This property(function) returns the name of a file (on disk) with its extension.
		Ex. `Screenshot_from_2020_hGETyTo.png` or `Screenshot_from_2020.png`
		"""
		import os

		return os.path.basename(self.file.name)

	@cached_property
	def title(self):
		"""Get alternate name that can be used for the photo in template."""
		return self.actual_filename.split('.')[0]


class Comment(models.Model):
	flags = GenericRelation(Flag)
	content = models.TextField()
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
	posted_datetime = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime'])
		]

	def __str__(self):
		return self.content


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

	LEVELS = (
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
	)

	COMMERCIAL = 'COMM'
	GENERAL = 'GEN'
	TECHNICAL = 'TECH'

	TYPES = (
		(COMMERCIAL, _('Commercial')),
		(GENERAL, _('General')),
		(TECHNICAL, _('Technical'))
	)
	
	level = models.CharField(max_length=5, choices=LEVELS)
	type = models.CharField(max_length=5, choices=TYPES, default='GEN')
	title = models.CharField(max_length=100)
	slug = models.SlugField(max_length=250)
	flags = GenericRelation(Flag)
	# actual file corresponding to past paper
	file = models.FileField(blank=True, upload_to=PAST_PAPERS_UPLOAD_DIR)
	poster = models.ForeignKey(
		User,
		on_delete=models.SET(get_dummy_user),
		related_name='past_papers',
		related_query_name='past_paper'
	) 
	# should be nullable..
	school = models.ForeignKey(
		Institution,
		on_delete=models.SET_NULL,
		related_name='past_papers',
		related_query_name='past_paper',
		null=True, blank=True
	)
	subject = models.ForeignKey(
		Subject,
		on_delete=models.PROTECT,
		related_name='past_papers',
		related_query_name='past_paper',
		blank=True, null=True
	)
	posted_datetime = models.DateTimeField(auto_now_add=True)
	# those with null=True will be considered as revision papers..
	written_date = models.DateField(null=True, blank=True)  # when the past paper was written..
	default_language = models.CharField(choices=settings.LANGUAGES, default='en', max_length=2)

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.title)
		return super().save(*args, **kwargs)

	def get_absolute_url(self, with_slug=True):
		if with_slug:
			return reverse('past_papers:past-paper-detail', kwargs={'pk': self.id, 'slug': self.slug})
		return reverse('past_papers:past-paper-detail', kwargs={'pk': self.id})

	@property
	def num_comments(self):
		return self.comments.count()

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

