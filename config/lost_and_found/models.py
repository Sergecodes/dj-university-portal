from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from core.constants import (
	LOST_ITEMS_PHOTOS_UPLOAD_DIR,
	LOST_OR_FOUND_ITEM_VALIDITY_PERIOD as VALIDITY_PERIOD
)
from core.model_fields import LowerCaseEmailField, TitleCaseField
from marketplace.models import Institution
# from taggit.managers import TaggableManager
from users.models import PhoneNumber

User = get_user_model()


class Post(models.Model):
	# tags will be obtained from the name of the item. ex. red pen => 'red', 'pen'
	# tags = TaggableManager()
	# i don't see the need for tags. todo search via normal field with search vector(Postgres) form more efficiency
	slug = models.SlugField(max_length=100)
	posted_datetime = models.DateTimeField(auto_now_add=True)
	# when the post will be considered expired. see save method for implementation
	expiry_datetime = models.DateTimeField()
	original_language = models.CharField(choices=settings.LANGUAGES, max_length=2, default='en')
	contact_name = TitleCaseField(
		_('Full name'),
		max_length=25,
		help_text=_('Please use your real names.'),
		# validators=[validate_full_name]
	)
	contact_numbers = models.ManyToManyField(
		PhoneNumber,
		related_name='+'
	)
	contact_email = LowerCaseEmailField(
		_('Email address'),
		max_length=50,
		help_text=_("Email address to contact; enter a valid email."),
		validators=[validate_email]
	)

	def save(self, *args, **kwargs):
		if not self.id:
			# since object hasn't yet been saved, its posted_datetime field will be None.
			# set it to appropriate value
			self.posted_datetime = timezone.now()
			self.expiry_datetime = self.posted_datetime + VALIDITY_PERIOD
		return super().save(*args, **kwargs)

	@property
	def is_outdated(self):
		"""Returns whether a post is outdated(has expired)"""
		return self.expiry_datetime < timezone.now()

	class Meta:
		abstract = True


class FoundItem(Post):
	item_found = models.CharField(max_length=100, help_text=_('What have you found?'))
	area_found = models.CharField(max_length=250, help_text=_('Where did you find the item?'))
	how_found = models.TextField(help_text=_('Explain how you found the item'))
	school = models.ForeignKey(
		Institution,
		on_delete=models.CASCADE,
		related_name='found_items',
		related_query_name='found_item'
	)
	poster = models.ForeignKey(
		User, 
		on_delete=models.CASCADE,
		related_name='found_items',
		related_query_name='found_item'
	)

	def __str__(self):
		return self.item_found

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.item_found)
		return super().save(*args, **kwargs)

	def get_absolute_url(self):
		return reverse('lost_and_found:found-item-detail', kwargs={'pk': self.id, 'slug': self.slug})

	class Meta:
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime']),
		]


class LostItem(Post):
	item_lost = models.CharField(max_length=100, help_text=_('What have you lost?'))
	item_description = models.TextField(help_text=_('Describe the lost item stating its important aspects.'))
	area_lost = models.CharField(max_length=250, help_text=_('Where do you think you lost the item?'))
	how_lost = models.TextField(help_text=_('Explain how you think you lost the item, stating areas you passed across or visited'), default=_('Good day, ... '))
	bounty = models.CharField(
		max_length=100,
		null=True, blank=True, 
		help_text=_('Award/bounty given to the person who will return the item. Make sure that you are in possession of the award. <br> This is optional but can be used as motivation.')
	)
	school = models.ForeignKey(
		Institution,
		on_delete=models.CASCADE,
		related_name='lost_items',
		related_query_name='lost_item'
	)
	poster = models.ForeignKey(
		User, 
		on_delete=models.CASCADE,
		related_name='lost_items',
		related_query_name='lost_item'
	)

	def __str__(self):
		return self.item_lost

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.item_lost)
		return super().save(*args, **kwargs)

	def get_absolute_url(self):
		return reverse('lost_and_found:lost-item-detail', kwargs={'pk': self.id, 'slug': self.slug})

	class Meta:
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime']),
		]


class LostItemPhoto(models.Model):
	# name of photo on disk (name without extension)
	# this field will actually never be blank. it is blank because we first need to save the file on disk before it's value will be known
	# title = models.CharField(max_length=60, null=True, blank=True) 
	file = models.ImageField(upload_to=LOST_ITEMS_PHOTOS_UPLOAD_DIR)
	upload_datetime = models.DateTimeField(auto_now_add=True)
	lost_item = models.ForeignKey(
		LostItem,
		on_delete=models.CASCADE,
		related_name='photos',
		related_query_name='photo',
		null=True, blank=True  
	)

	def __str__(self):
		return self.file.name  

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
		return self.actual_filename.split('.')[0]

	# def save(self, *args, **kwargs):
	# 	# first save and store file in storage
	# 	super().save(*args, **kwargs)

	# 	# set title of file if it hasn't yet been saved
	# 	if not self.title:
	# 		self.title = self.actual_filename.split('.')[0]
	# 		self.save(update_fields=['title'])
			
	# 	return self

	class Meta:
		verbose_name = 'Lost Items Photo'
		verbose_name_plural = 'Lost Items Photos'

