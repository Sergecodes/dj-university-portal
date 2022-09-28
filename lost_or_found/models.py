from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import capfirst, truncatewords
from django.urls import reverse
from django.utils.module_loading import import_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField

from core.constants import LOST_ITEMS_PHOTOS_UPLOAD_DIR, MAX_TEXT_LENGTH
from core.models import Post, City
from core.utils import PhotoModelMixin

STORAGE = import_string(settings.DEFAULT_FILE_STORAGE)()
User = get_user_model()


class LostItem(Post):
	item_lost = models.CharField(
		_('Item lost'), 
		max_length=100, 
		help_text=_('What have you lost?'),
		unique=True
	)
	item_description = models.TextField(
		_('Item description'), 
		help_text=_('Describe the lost item stating its important aspects.'),
		max_length=MAX_TEXT_LENGTH
	)
	area_lost = models.CharField(
		_('Area lost'), 
		max_length=250, 
		help_text=_('Where do you think you lost the item?')
	)
	how_lost = models.TextField(
		_('How lost'), 
		help_text=_(
			'Explain how you think you lost the item, ' 
			'stating areas you passed across or visited'
		), 
		default=_('Good day, '),
		max_length=MAX_TEXT_LENGTH
	)
	bounty = models.CharField(
		_('Bounty'),
		max_length=100,
		blank=True, 
		help_text=_(
			'Award/bounty given to the person who will return the item. '
			'Make sure that you are in possession of the award. <br> '
			'This is optional but can be used as motivation.'
		)
	)
	city = models.ForeignKey(
		City,
		on_delete=models.CASCADE,
		related_name='lost_items',
		related_query_name='lost_item',
		help_text=_('City where item was lost')
	)
	poster = models.ForeignKey(
		User, 
		on_delete=models.CASCADE,
		related_name='lost_items',
		related_query_name='lost_item'
	)
	# no property @bookmark_count coz the parent class 
	# already creates it.
	bookmarkers = models.ManyToManyField(
		User,
		related_name='bookmarked_lost_items',
		related_query_name='bookmarked_lost_item',
		blank=True
	)

	def __str__(self):
		return self.item_lost

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.item_lost)
		self.item_lost = capfirst(self.item_lost)
		super().save(*args, **kwargs)

	def get_absolute_url(self, with_slug=True):
		if with_slug: 
			return reverse('lost_or_found:lost-item-detail', kwargs={'pk': self.id, 'slug': self.slug})
		return reverse('lost_or_found:lost-item-detail', kwargs={'pk': self.id})

	class Meta:
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime']),
		]


class LostItemPhoto(models.Model, PhotoModelMixin):
	file = ThumbnailerImageField(
		thumbnail_storage=STORAGE, 
		upload_to=LOST_ITEMS_PHOTOS_UPLOAD_DIR
	)
	upload_datetime = models.DateTimeField(auto_now_add=True)
	lost_item = models.ForeignKey(
		LostItem,
		on_delete=models.CASCADE,
		related_name='photos',
		related_query_name='photo',
		null=True, blank=True  
	)

	def __str__(self):
		return self.actual_filename

	class Meta:
		verbose_name = 'Lost Item Photo'
		verbose_name_plural = 'Lost Items Photos'


class FoundItem(Post):
	item_found = models.CharField(
		_('Item found'), 
		max_length=100, 
		help_text=_('What have you found?'),
		unique=truncatewords
	)
	area_found = models.CharField(
		_('Area found'), 
		max_length=250, 
		help_text=_('Where did you find the item?')
	)
	how_found = models.TextField(
		_('How found'), 
		help_text=_('Explain how you found the item'),
		max_length=MAX_TEXT_LENGTH
	)
	city = models.ForeignKey(
		City,
		help_text=_('City where item was found'),
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
	bookmarkers = models.ManyToManyField(
		User,
		related_name='bookmarked_found_items',
		related_query_name='bookmarked_found_item',
		blank=True
	)

	def __str__(self):
		return self.item_found

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.item_found)
		self.item_found = capfirst(self.item_found)
		super().save(*args, **kwargs)

	def get_absolute_url(self, with_slug=True):
		if with_slug: 
			return reverse('lost_or_found:found-item-detail', kwargs={'pk': self.id, 'slug': self.slug})
		return reverse('lost_or_found:found-item-detail', kwargs={'pk': self.id})

	class Meta:
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime']),
		]

