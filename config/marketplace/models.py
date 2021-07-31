from ckeditor.fields import RichTextField
from datetime import timedelta
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
# from django.core.validators import validate_email
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.model_fields import LowerCaseEmailField, TitleCaseField
from hitcount.models import HitCountMixin

User = settings.AUTH_USER_MODEL


class AdCategory(models.Model):
	name = models.CharField(_('Name'), max_length=35)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Ad Categories'


class ItemSubCategory(models.Model):
	name = models.CharField(_('Name'), max_length=35)
	parent_category = models.ForeignKey(
		'ItemCategory', 
		on_delete=models.PROTECT,  # prevent deletion of group if it contains some categories
		related_name='sub_categories',
		related_query_name='sub_category'
	)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Item Subcategories'


class ItemCategory(models.Model):
	name = models.CharField(_('Name'), max_length=30)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Item Categories'


class ItemListingPhoto(models.Model):
	title = models.CharField(max_length=255, blank=True, null=True)
	file = models.ImageField(upload_to='item_photos/')
	upload_datetime = models.DateTimeField(auto_now_add=True)
	
	# many item_listing_photos can belong to one item_listing...
	item_listing = models.ForeignKey(
		'ItemListing',
		on_delete=models.CASCADE,
		related_name='images',
		related_query_name='image',
		null=True, blank=True   # change this !!
	)

	def __str__(self):
		return self.file.name

	# def save(self, *args, **kwargs):
	# 	self.title = self.file.name.split('/')[1]
	# 	super().save(*args, **kwargs)


	class Meta:
		verbose_name = 'Item Listing Photo'
		verbose_name_plural = 'Item Listing Photos'


class AdPhoto(models.Model):
	image = models.ImageField(upload_to='ad photos')
	ad = models.ForeignKey(
		'Ad',
		on_delete=models.CASCADE,
		related_name='images',
		related_query_name='image'
	)

	class Meta:
		verbose_name_plural = 'Ad Photos'


class Post(models.Model):
	THREE_DAYS = timedelta(days=3)
	FIVE_DAYS = timedelta(days=5)
	ONE_WEEK = timedelta(weeks=1)
	TEN_DAYS = timedelta(days=10)
	ONE_MONTH = timedelta(weeks=4)
	# THREE_MONTHS = timedelta(weeks=4 * 3)
	# FIVE_MONTHS = timedelta(weeks=4 * 5)
	# UNLIMITED = timedelta(weeks=52)  # one year

	DURATION_OPTIONS = (
		(THREE_DAYS, _('3 days')),
		(FIVE_DAYS, _('5 days')),
		(ONE_WEEK, _('1 week')),
		(TEN_DAYS, _('10 days')),
		(ONE_MONTH, _('1 month')),
		# (THREE_MONTHS, _('3 months')),
		# (FIVE_MONTHS, _('5 months')),
		# (UNLIMITED, _('One whole year'))
	)

	duration = models.DurationField(
		choices=DURATION_OPTIONS, 
		default=FIVE_DAYS,
		help_text=_('For how long should your post be available')
	)
	# email address to contact for any info concerning this post.
	# in frontend form, this is by default the email of the user creating the listing
	contact_email = LowerCaseEmailField(
		_('Email address'),
		max_length=50,
		help_text=_("Email address to use for notifications"),
		# validators=[validate_email]
	)
	contact_name = TitleCaseField(
		_('Full name'),
		max_length=25,
		help_text=_('Enter real names, buyers will more easily trust you if you enter a real name.'),
		# validators=[validate_full_name]
	)
	contact_numbers = GenericRelation('users.PhoneNumber')
	# delete post if user is deleted
	owner = models.OneToOneField(User, on_delete=models.CASCADE)
	title = models.CharField(
		_('Title'), 
		max_length=80, 
		help_text=_('A descriptive title helps buyers find your item. <br> State exactly what your post is.')
	)
	slug = models.SlugField()
	description = RichTextField(
		_('Description'), 
		help_text=_('Describe the your post and provide complete and accurate details. Use a clear and concise format.')
	)
	datetime_added = models.DateTimeField(_('Date/time added'), auto_now_add=True)
	# language in which post was created 
	# in template form, default language should be user's current language code (passed as a hidden field)
	original_language = models.CharField(
		_('Initial language'),
		choices=settings.LANGUAGES,
		default='fr', 
		max_length=3,
		help_text=_('Initial language in which post was entered in.')
	)

	def __str__(self):
		return self.title

	@property
	def is_active(self):
		""" Post is active if duration is not yet exhausted """
		return (timezone.now() - self.duration).total_seconds() > 0

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.title)
		super().save(*args, **kwargs)

	class Meta:
		abstract = True


class ItemListing(Post, HitCountMixin):
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

	category = models.ForeignKey(
		'ItemCategory', 
		related_name='item_listings', 
		related_query_name='item_listing',
		on_delete=models.PROTECT
	)
	condition = models.CharField(
		max_length=3,
		choices=CONDITIONS,
		default=NEW,
		help_text=_("Select the condition of the item you're listing.")
	)
	condition_description = models.TextField(
		_('Condition description'),
		help_text=_('Provide details about the condition of a non brand-new item, including any defects or flaws, so that buyers know exactly what to expect.'),
		null=True, blank=True
	)
	price = models.PositiveIntegerField(
		_('Price'), 
		help_text=_("Figures and spaces only, no commas or dots. <br> Enter <b>0</b> for free products or services."),
	)
	institution = models.ForeignKey(
		'Institution',
		on_delete=models.CASCADE,
		related_name='item_listings',
		related_query_name='item_listing'
	)


	def get_absolute_url(self):
		""" Returns the url to access a detail record for this item. """
		return reverse('marketplace:item-detail', kwargs={'id': self.id, 'slug': self.slug})

	@property
	def view_count(self):
		return self.hitcount.num_of_hits

	class Meta:
		verbose_name_plural = 'Item Listings'


class Ad(Post, HitCountMixin):
	category = models.OneToOneField('AdCategory', on_delete=models.PROTECT)
	price = models.CharField(
		_('Price'), 
		help_text=_("Figures and spaces only, no commas or dots. <br> Enter <b>-</b> for free products or services, or if the price is part of the description."),
		default='-',
		max_length=15
	)
	institution = models.ForeignKey(
		'Institution',
		on_delete=models.CASCADE,
		related_name='ads',
		related_query_name='ad',
		null=True, blank=True,
		help_text=_('Allow this empty if this ad concerns no particular institution.')
	)

	def get_absolute_url(self):
		""" Returns the url to access a detail record for this item. """
		return reverse('marketplace:ad-detail', kwargs={'id': self.id, 'slug': self.slug})

	@property
	def view_count(self):
		return self.hitcount.num_of_hits


class Institution(models.Model):
	# only staff can add school.
	name = models.CharField(_('Name'), max_length=50)
	location = models.CharField(
		_('Location'),
		max_length=40,
		help_text=_('Street or quarter where institution is located')
	)
	datetime_added = models.DateTimeField(_('Date/time added'), auto_now_add=True)

	def __str__(self):
		return self.name

