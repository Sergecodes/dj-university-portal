from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import capfirst
from django.urls import reverse
from django.utils.text import slugify
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField

from core.constants import REQUESTED_ITEMS_PHOTOS_UPLOAD_DIR, MAX_TEXT_LENGTH
from core.models import Post, City
from core.utils import PhotoModelMixin
from marketplace.models import ItemCategory

STORAGE = import_string(settings.DEFAULT_FILE_STORAGE)()
User = get_user_model()


class RequestedItem(Post):
	category = models.ForeignKey(
		ItemCategory, 
		verbose_name=_('Category'),
		related_name='requested_items', 
		related_query_name='requested_item',
		on_delete=models.RESTRICT
	)
	item_requested = models.CharField(
		_('Item requested'), 
		max_length=100, 
		help_text=_('What item do you need?'),
		unique=True
	)
	item_description = models.TextField(
		_('Item description'), 
		help_text=_(
			'Describe the item you are in need of, stating its important aspects. <br>'
			'You may allow this field empty.'
		),
		blank=True,
		max_length=MAX_TEXT_LENGTH
	)
	price_at_hand = models.CharField(
		_('Price at hand'),
		max_length=20,
		default='-',
		help_text=_('How much are you willing to pay for the item? You may allow this field empty.')
	)
	city = models.ForeignKey(
		City,
		verbose_name=_('City of residence'),
		on_delete=models.CASCADE,
		related_name='requested_items',
		related_query_name='requested_item',
	)
	poster = models.ForeignKey(
		User, 
		on_delete=models.CASCADE,
		related_name='requested_items',
		related_query_name='requested_item'
	)
	bookmarkers = models.ManyToManyField(
		User,
		related_name='bookmarked_requested_items',
		related_query_name='bookmarked_requested_item',
		blank=True
	)

	def __str__(self):
		return self.item_requested

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.item_requested)
		self.item_requested = capfirst(self.item_requested)
		super().save(*args, **kwargs)

	def get_absolute_url(self, with_slug=True):
		if with_slug: 
			return reverse('requested_items:requested-item-detail', kwargs={'pk': self.pk, 'slug': self.slug})
		return reverse('requested_items:requested-item-detail', kwargs={'pk': self.pk})

	class Meta:
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime']),
		]


class RequestedItemPhoto(models.Model, PhotoModelMixin):
	file = ThumbnailerImageField(
		thumbnail_storage=STORAGE,
		upload_to=REQUESTED_ITEMS_PHOTOS_UPLOAD_DIR
	)
	upload_datetime = models.DateTimeField(auto_now_add=True)
	requested_item = models.ForeignKey(
		RequestedItem,
		on_delete=models.CASCADE,
		related_name='photos',
		related_query_name='photo',
		null=True, blank=True  
	)

	def __str__(self):
		return self.actual_filename

	class Meta:
		verbose_name = 'Requested Item Photo'
		verbose_name_plural = 'Requested Items Photos'

