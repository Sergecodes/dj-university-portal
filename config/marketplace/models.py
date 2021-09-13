from ckeditor.fields import RichTextField
from datetime import timedelta
from django.conf import settings
# from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import validate_email
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.constants import (
	AD_PHOTOS_UPLOAD_DIR, 
	LISTING_PHOTOS_UPLOAD_DIR
)
from core.model_fields import LowerCaseEmailField, TitleCaseField
from hitcount.models import HitCountMixin

User = settings.AUTH_USER_MODEL


class AdCategory(models.Model):
	name = models.CharField(_('Name'), max_length=35)
	datetime_added = models.DateTimeField(auto_now_add=True)

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
	datetime_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Item Subcategories'


class ItemCategory(models.Model):
	name = models.CharField(_('Name'), max_length=30)
	datetime_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Item Categories'


class ItemListingPhoto(models.Model):
	# name of photo on disk (name without extension)
	# this field will actually never be blank. it is blank because we first need to save the file on disk before it's value will be known
	# title = models.CharField(max_length=60, null=True, blank=True) 
	file = models.ImageField(upload_to=LISTING_PHOTOS_UPLOAD_DIR)
	upload_datetime = models.DateTimeField(auto_now_add=True)
	
	# many item_listing_photos can belong to one item_listing...
	item_listing = models.ForeignKey(
		'ItemListing',
		on_delete=models.CASCADE,
		related_name='photos',
		related_query_name='photo',
		null=True, blank=True  
		# in reality, each photo should belong to a listing. null is set here because when uploading a photo, there was no way to link the saved photo to an unsaved(yet) listing instance. thus we save the photo first without a listing instance, then save the listing, then link the photo to the listing. thus in our db, we should always have a photo linked to an item listing.

		# To prevent the event of a user uploading photos but not submitting a listing: 
		# attach window.onunload event to page. if user clicks on submit button, we save a cookie ('clickedSubmit'). if he leaves page without clicking submit button(if there's no such cookie), send ajax request to server to delete photos that have been uploaded(can do so using session in backend..). Ultimately remove cookie.
		#  the above will probably be unneccessary and will probably cause some server load. it should be done only if storage space is a concern.
	)

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
		verbose_name = 'Item Listing Photo'
		verbose_name_plural = 'Item Listing Photos'


class AdListingPhoto(models.Model):
	# title = models.CharField(max_length=60, null=True, blank=True) 
	file = models.ImageField(upload_to=AD_PHOTOS_UPLOAD_DIR)
	upload_datetime = models.DateTimeField(auto_now_add=True)
	ad_listing = models.ForeignKey(
		'AdListing',
		on_delete=models.CASCADE,
		related_name='photos',
		related_query_name='photo',
		null=True, blank=True  # same reason as above
	)

	class Meta:
		verbose_name_plural = 'Ad Listing Photos'

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
		return self.actual_filename.split('.')[0]

	# def save(self, *args, **kwargs):
	# 	# first save and store file in storage
	# 	super().save(*args, **kwargs)

	# 	# set title of file if it hasn't yet been saved
	# 	if not self.title:
	# 		self.title = self.actual_filename.split('.')[0]
	# 		self.save(update_fields=['title'])

	# 	return self


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
		default=ONE_MONTH,
		help_text=_('For how long should your post be available')
	)
	# email address to contact for any info concerning this post.
	# in frontend form, this is by default the email of the user creating the listing
	contact_email = LowerCaseEmailField(
		_('Email address'),
		max_length=50,
		help_text=_("Email address to contact; enter a valid email"),
		validators=[validate_email]
	)
	contact_name = TitleCaseField(
		_('Full name'),
		max_length=25,
		help_text=_('Enter real names, buyers will more easily trust you if you enter a real name.'),
		# validators=[validate_full_name]
	)
	# contact_numbers = GenericRelation('users.PhoneNumber')
	# since title isn't unique, slug can't be used to get a particular object.
	# also, querying on slug (char field) is slower than on ints (id) and if we set title to unique, there will be overhead when saving an instance(to check if it is unique.)
	title = models.CharField(
		_('Title'), 
		max_length=100, 
		help_text=_('A descriptive title helps buyers find your item. <br> State exactly what your post is.')
	)
	slug = models.SlugField(max_length=255)
	description = RichTextField(
		_('Description'), 
		help_text=_('Describe the your post and provide complete and accurate details. Use a clear and concise format.')
	)
	datetime_added = models.DateTimeField(_('Date/time added'), auto_now_add=True)
	updated_datetime = models.DateTimeField(auto_now=True, editable=False)
	# language in which post was created 
	original_language = models.CharField(
		_('Initial language'),
		choices=settings.LANGUAGES,
		default='fr', 
		max_length=3,
		help_text=_('Initial language in which post was entered.')
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
	USED = 'U'
	NEW = 'N'
	DEFECTIVE = 'D'
	CONDITIONS = (
		(NEW, _('New')),  # maybe not packaged but not yet used or fairly used (still new)
		(USED, _('Used')),  # already used but still working
		(DEFECTIVE, _('Defective(some parts are not working)'))  # for parts or not working
	)

	contact_numbers = models.ManyToManyField(
		'users.PhoneNumber',
		related_name='+'
	)
	# delete listing if user is deleted
	owner = models.ForeignKey(
		User, 
		on_delete=models.CASCADE,
		related_name='item_listings',
		related_query_name='item_listing'
	)
	institution = models.ForeignKey(
		'Institution',
		on_delete=models.CASCADE,
		related_name='item_listings',
		related_query_name='item_listing'
	)
	category = models.ForeignKey(
		'ItemCategory', 
		related_name='item_listings', 
		related_query_name='item_listing',
		on_delete=models.PROTECT
	)
	sub_category = models.ForeignKey(
		'ItemSubCategory', 
		related_name='item_listings', 
		related_query_name='item_listing',
		on_delete=models.PROTECT,
		null=True, blank=True,
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
	# in form, field will be displayed as charfield. this is to enable entering of spaces..
	price = models.PositiveIntegerField(
		_('Price'), 
		help_text=_("Figures and spaces only, no commas or dots. <br> Enter <b>0</b> for free products or services."),
	)


	def get_absolute_url(self):
		""" Returns the url to access a detail record for this item. """
		return reverse('marketplace:item-listing-detail', kwargs={'pk': self.id, 'slug': self.slug})

	@property
	def view_count(self):
		return self.hitcount.num_of_hits

	class Meta:
		verbose_name_plural = 'Item Listings'
		ordering = ['-datetime_added']
		indexes = [
			models.Index(fields=['-datetime_added'])
		]


class AdListing(Post, HitCountMixin):
	contact_numbers = models.ManyToManyField(
		'users.PhoneNumber',
		related_name='+'
	)
	owner = models.ForeignKey(
		User, 
		on_delete=models.CASCADE,
		related_name='ad_listings',
		related_query_name='ad_listing'
	)
	category = models.ForeignKey(
		'AdCategory', 
		related_name='ad_listings', 
		related_query_name='ad_listing',
		on_delete=models.PROTECT
	)
	pricing = models.CharField(
		_('Pricing'), 
		help_text=_("Allow this empty for free products and services or if the pricing is in the advert description."),
		null=True, blank=True,
		default='-',
		max_length=20
	)
	institution = models.ForeignKey(
		'Institution',
		on_delete=models.CASCADE,
		related_name='ad_listings',
		related_query_name='ad_listing',
		null=True, blank=True,
		help_text=_('Allow this empty if this advert concerns no particular institution.')
	)

	def get_absolute_url(self):
		""" Returns the url to access a detail record for this item. """
		return reverse('marketplace:ad-listing-detail', kwargs={'pk': self.id, 'slug': self.slug})

	@property
	def view_count(self):
		return self.hitcount.num_of_hits

	class Meta:
		ordering = ['-datetime_added']
		indexes = [
			models.Index(fields=['-datetime_added'])
		]


class Institution(models.Model):
	# only staff can add school.
	name = models.CharField(_('Name'), max_length=50, unique=True)
	location = models.CharField(
		_('Location'),
		max_length=40,
		help_text=_('Street or quarter where institution is located')
	)
	datetime_added = models.DateTimeField(_('Date/time added'), auto_now_add=True)

	def __str__(self):
		return self.name

