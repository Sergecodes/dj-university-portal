from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import capfirst
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.constants import LOST_ITEMS_PHOTOS_UPLOAD_DIR
from core.models import Post, Institution

User = get_user_model()


class FoundItem(Post):
	item_found = models.CharField(
		_('Item found'), 
		max_length=100, 
		help_text=_('What have you found?')
	)
	area_found = models.CharField(
		_('Area found'), 
		max_length=250, 
		help_text=_('Where did you find the item?')
	)
	how_found = models.TextField(_('How found'), help_text=_('Explain how you found the item'))
	school = models.ForeignKey(
		Institution,
		verbose_name=_('School'),
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
		self.item_found = capfirst(self.item_found)
		super().save(*args, **kwargs)

	def get_absolute_url(self, with_slug=True):
		if with_slug: 
			return reverse('lost_and_found:found-item-detail', kwargs={'pk': self.id, 'slug': self.slug})
		return reverse('lost_and_found:found-item-detail', kwargs={'pk': self.id})

	class Meta:
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime']),
		]


class LostItem(Post):
	item_lost = models.CharField(_('Item lost'), max_length=100, help_text=_('What have you lost?'))
	item_description = models.TextField(
		_('Item description'), 
		help_text=_('Describe the lost item stating its important aspects.')
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
		default=_('Good day, ... ')
	)
	bounty = models.CharField(
		_('Bounty'),
		max_length=100,
		null=True, blank=True, 
		help_text=_(
			'Award/bounty given to the person who will return the item. '
			'Make sure that you are in possession of the award. <br> '
			'This is optional but can be used as motivation.'
		)
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
		self.item_lost = capfirst(self.item_lost)
		super().save(*args, **kwargs)

	def get_absolute_url(self, with_slug=True):
		if with_slug: 
			return reverse('lost_and_found:lost-item-detail', kwargs={'pk': self.id, 'slug': self.slug})
		return reverse('lost_and_found:lost-item-detail', kwargs={'pk': self.id})

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

	class Meta:
		verbose_name = 'Lost Item Photo'
		verbose_name_plural = 'Lost Items Photos'

