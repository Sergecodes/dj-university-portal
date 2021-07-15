from ckeditor.fields import RichTextField
from datetime import timedelta
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from hitcount.models import HitCount, HitCountMixin


User = settings.AUTH_USER_MODEL


class Category(models.Model):
	name = models.CharField(_('Name'), max_length=35)
	# prevent deletion of group if it contains some categories
	group = models.ForeignKey('ParentCategory', on_delete=models.PROTECT, verbose_name=_('Group'))

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Categories'


class ParentCategory(models.Model):
	name = models.CharField(_('Name'), max_length=30)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Parent Categories'


class Post(models.Model):
	# TODO when getting post in views, ensure not to get posts of deleted users.
	# ONE_DAY = timedelta(days=1)
	# THREE_DAYS = timedelta(days=3)
	FIVE_DAYS = timedelta(days=5)
	ONE_WEEK = timedelta(weeks=1)
	TEN_DAYS = timedelta(days=10)

	# PAID
	ONE_MONTH = timedelta(weeks=4)
	THREE_MONTHS = timedelta(weeks=4 * 3)
	FIVE_MONTHS = timedelta(weeks=4 * 5)
	# UNLIMITED = timedelta(weeks=52)  # one year

	DURATION_OPTIONS = (
		# (THREE_DAYS, _('3 days')),
		(FIVE_DAYS, _('5 days')),
		(ONE_WEEK, _('1 week')),
		(TEN_DAYS, _('10 days')),

		(ONE_MONTH, _('1 month')),
		(THREE_MONTHS, _('3 months')),
		(FIVE_MONTHS, _('5 months')),
		# (UNLIMITED, _('One whole year'))
	)

	duration = models.DurationField(choices=DURATION_OPTIONS, default=FIVE_DAYS)
	owner = models.OneToOneField(User, on_delete=models.CASCADE)
	category = models.OneToOneField('Category', on_delete=models.PROTECT)
	title = models.CharField(_('Title'), max_length=30)
	slug = models.SlugField()
	description = RichTextField()
	datetime_added = models.DateTimeField(_('Date/time added'), auto_now_add=True)
	number_of_bookmarks = models.PositiveIntegerField(_('Number of bookmarks'), default=0)
	institution = models.ForeignKey(
		'Institution',
		on_delete=models.CASCADE,
		related_name='%(class)s_posts',
		related_query_name='post'
	)
	# language in which post was created
	language = models.CharField(
		_('Language'),
		choices=settings.LANGUAGES,
		default='en',  # in template form, default language should be user's current language or first language
		max_length=3
	)

	# def bookmark(self):
	#     self.bookmarks = models.F('number_of_bookmarks') + 1
	#     self.save(update_fields=['number_of_bookmarks'])

	# def remove_bookmark(self):
	#     self.bookmarks = models.F('number_of_bookmarks') - 1
	#     self.save(update_fields=['number_of_bookmarks'])

	def __str__(self):
		return self.title

	# def get_absolute_url(self):
	# 	""" Returns the url to access a detail record for this item. """
	# 	return reverse('post-detail', args=[str(self.id), self.slug])

	@property
	def is_active(self):
		""" Post is active if duration is not yet exhausted """
		return (timezone.now() - self.duration).total_seconds() > 0

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.title)
		# self.school.num_of_items = F('num_of_items') + 1
		super().save(*args, **kwargs)

	class Meta:
		abstract = True


class Item(Post, HitCountMixin):
	BRAND_NEW = 'BN'
	USED = 'U'
	NEW = 'N'
	DEFECTIVE = 'D'
	CONDITIONS = (
		(BRAND_NEW, _('Brand new')),  # still packaged...
		(USED, _('Used')),  # already used
		(NEW, _('New')),  # maybe not packaged but not yet used or fairly used (still new)
		(DEFECTIVE, _('For parts or not working'))
	)
	# TODO see how ebay listing form looks like and modify accordingly

	condition = models.CharField(
		max_length=2,
		choices=CONDITIONS,
		default=NEW,
		help_text=_("Select the condition of the item you're listing")
	)
	condition_description = models.TextField(
		_('Condition description'),
		help_text=_('Provide details about the condition of a non brand new item, including any defects or flaws, '
					'so that buyers know exactly what to expect.')
	)
	hitcount_generic = GenericRelation(
		HitCount,
		object_id_field='object_id',
		related_query_name='item'
	)
	# to enable getting the items that a user has bookmarked(user.bookmarked_items) and also probably the
	# number of people that have bookmarked a user's item ?
	# TODO owners won't be able to see those who bookmarked their posts, but may see number of bookmarks
	# means if User is deleted, set  it/bookmarker(User) to NULL
	bookmarkers = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		blank=True, null=True,
		related_name='bookmarked_posts',
		related_query_name='bookmarked_post'
	)

	def get_absolute_url(self):
		""" Returns the url to access a detail record for this item. """
		return reverse('item-detail', args=[str(self.id), self.slug])

	@property
	def view_count(self):
		return self.hitcount.num_of_hits


class Ad(Post, HitCountMixin):
	hitcount_generic = GenericRelation(
		HitCount,
		object_id_field='object_id',
		related_query_name='ad'
	)
	bookmarkers = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		blank=True, null=True,
		related_name='bookmarked_ads',
		related_query_name='bookmarked_ad'
	)

	def get_absolute_url(self):
		""" Returns the url to access a detail record for this item. """
		return reverse('ad-detail', args=[str(self.id), self.slug])

	@property
	def view_count(self):
		return self.hitcount.num_of_hits


class Institution(models.Model):
	# only staff can add school.
	name = models.CharField(_('Name'), max_length=40)
	location = models.CharField(
		_('Location'),
		max_length=20,
		help_text=_('Street or quarter where institution is located')
	)
	datetime_added = models.DateTimeField(_('Date/time added'), auto_now_add=True)

	# num_of_items = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.name
