from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants import IMAGE_HOLDER_UPLOAD_DIR
from core.model_fields import DynamicStorageImageField, NormalizedEmailField
from core.utils import PhotoModelMixin
from flagging.models import Flag


class Institution(models.Model):
	# only staff can add school.
	name = models.CharField(_('Name'), max_length=50, unique=True)
	location = models.CharField(
		_('Location'),
		max_length=60,
		help_text=_('Street or quarter where institution is located')
	)
	datetime_added = models.DateTimeField(_('Date/time added'), auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name


class Post(models.Model):
	"""Abstract model to describe an item post."""

	flags = GenericRelation(Flag)
	view_count = models.PositiveIntegerField(default=0)
	slug = models.SlugField(max_length=255)
	posted_datetime = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)
	# when the post will be considered expired. see save method for implementation
	# expiry_datetime = models.DateTimeField()
	original_language = models.CharField(
		choices=settings.LANGUAGES,
		max_length=2,
		help_text=_('Language in which post was created'),
		editable=False
	)
	# to know if a post has been edited, you can use this field; 
	# it will be empty ('')
	update_language = models.CharField(
		choices=settings.LANGUAGES,
		max_length=2,
		help_text=_('Language in which last update was done'),
		editable=False,
		blank=True
	)
	contact_numbers = models.ManyToManyField(
		'users.PhoneNumber',
		related_name='+',
		verbose_name=_('Contact numbers')
	)
	contact_email = NormalizedEmailField(
		_('Email address'),
		max_length=50,
		help_text=_("Email address to contact; enter a valid email."),
		validators=[validate_email]
	)

	@property
	def bookmark_count(self):
		self.bookmarkers.count()

	class Meta:
		abstract = True


	# def save(self, *args, **kwargs):
	# 	if not self.id:
	# 		self.expiry_datetime = self.posted_datetime + VALIDITY_PERIOD
	# 	super().save(*args, **kwargs)

	# @property
	# def is_outdated(self):
	# 	"""Returns whether a post is outdated(has expired)"""
	# 	return self.expiry_datetime < timezone.now()


class ImageHolder(models.Model, PhotoModelMixin):
	"""Permit storing an image in storage to a model object."""
	# see https://stackoverflow.com/a/12917845/  
	# (answer to question programmatically saving image to Django ImageField)
	
	# this upload_to directory is useless, since this model is used with files that
	# have already been saved...
	width = models.PositiveIntegerField()
	height = models.PositiveIntegerField()
	file = DynamicStorageImageField(
		upload_to=IMAGE_HOLDER_UPLOAD_DIR,
		width_field='width', height_field='height',
	)
