from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.constants import LOST_OR_FOUND_ITEM_VALIDITY_PERIOD as VALIDITY_PERIOD
from core.model_fields import LowerCaseEmailField, TitleCaseField
from marketplace.models import Institution
from taggit.managers import TaggableManager
from users.models import PhoneNumber

User = get_user_model()


class Post(models.Model):
	# tags will be obtained from the name of the item. ex. red pen => 'red', 'pen'
	tags = TaggableManager()
	slug = models.SlugField(max_length=100)
	posted_datetime = models.DateTimeField(auto_now_add=True)
	original_language = models.CharField(choices=settings.LANGUAGES, max_length=2, default='en')
	is_outdated = models.BooleanField(default=False, editable=False)
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

	@property
	def expiry_datetime(self):
		"""When the post has to expire"""
		return self.posted_datetime + VALIDITY_PERIOD

	def is_outdated(self):
		"""Returns whether a post is outdated (has expired)"""
		return self.expiry_datetime < timezone.now()

	class Meta:
		abstract = True


class FoundItem(Post):
	item_found = models.CharField(max_length=50, help_text=_('What have you found'))
	area_found = models.CharField(max_length=100, help_text=_('Where did you find the item'))
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

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.item_found)
		return super().save(*args, **kwargs)

	def get_absolute_url(self):
		return reverse('lost_and_found:found-item-detail', kwargs={'pk': self.id, 'slug': self.slug})


class LostItem(Post):
	item_lost = models.CharField(max_length=50, help_text=_('What have you lost'))
	item_description = models.TextField(help_text=_('Describe the lost item stating the important aspects.'))
	area_lost = models.CharField(max_length=100, help_text=_('Where you think you lost the item'))
	how_lost = models.TextField(help_text=_('Explain how you think you lost the item, stating areas you passed across or visited'), default=_('Good day, '))
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

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.item_lost)
		return super().save(*args, **kwargs)

	def get_absolute_url(self):
		return reverse('lost_and_found:lost-item-detail', kwargs={'pk': self.id, 'slug': self.slug})
