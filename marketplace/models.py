from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import capfirst
from django.urls import reverse
from django.utils.module_loading import import_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField

from core.constants import AD_PHOTOS_UPLOAD_DIR, LISTING_PHOTOS_UPLOAD_DIR, MAX_TEXT_LENGTH
from core.models import Post, City
from core.utils import PhotoModelMixin

STORAGE = import_string(settings.DEFAULT_FILE_STORAGE)()
User = get_user_model()


class AdCategory(models.Model):
	name = models.CharField(_('Name'), max_length=35)
	datetime_added = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Ad Categories'


class ItemSubCategory(models.Model):
	name = models.CharField(_('Name'), max_length=35)
	parent_category = models.ForeignKey(
		'ItemCategory', 
		on_delete=models.RESTRICT,  # prevent deletion of group if it contains some categories
		related_name='sub_categories',
		related_query_name='sub_category'
	)
	datetime_added = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Item SubCategories'


class ItemCategory(models.Model):
	name = models.CharField(_('Name'), max_length=30)
	datetime_added = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Item Categories'


class ItemListingPhoto(models.Model, PhotoModelMixin):
	file = ThumbnailerImageField(
		thumbnail_storage=STORAGE, 
		upload_to=LISTING_PHOTOS_UPLOAD_DIR
	)
	upload_datetime = models.DateTimeField(auto_now_add=True)
	
	# many item_listing_photos can belong to one item_listing...
	item_listing = models.ForeignKey(
		'ItemListing',
		on_delete=models.CASCADE,
		related_name='photos',
		related_query_name='photo',
		null=True, blank=True  
	)
	# in reality, each photo should belong to a listing. 
	# null is set here because when uploading a photo, 
	# there was no way to link the saved photo to an unsaved(yet) listing instance. 
	# thus we save the photo first without a listing instance, then save the listing, 
	# then link the photo to the listing. 
	# thus in our db, we should always have a photo linked to an item listing.

	# To prevent the event of a user uploading photos but not submitting a listing: 
	# attach window.onunload event to page. if user clicks on submit button, 
	# we save a cookie ('clickedSubmit'). if he leaves page without clicking submit button
	# (if there's no such cookie), send ajax request to server to delete photos 
	# that have been uploaded(can do so using session in backend..). Ultimately remove cookie.
	#  the above will probably be unneccessary and will probably cause some server load. 
	# it should be done only if storage space is a concern.
	
	def __str__(self):
		return self.actual_filename
		
	class Meta:
		verbose_name = 'Item Listing Photo'
		verbose_name_plural = 'Item Listing Photos'


class AdListingPhoto(models.Model, PhotoModelMixin):
	file = ThumbnailerImageField(
		thumbnail_storage=STORAGE,
		upload_to=AD_PHOTOS_UPLOAD_DIR
	)
	upload_datetime = models.DateTimeField(auto_now_add=True)
	ad_listing = models.ForeignKey(
		'AdListing',
		on_delete=models.CASCADE,
		related_name='photos',
		related_query_name='photo',
		null=True, blank=True  # same reason as above
	)

	def __str__(self):
		return self.actual_filename

	class Meta:
		verbose_name_plural = 'Ad Listing Photos'


class ListingPost(Post):
	'''
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
	'''

	title = models.CharField(
		_('Title'), 
		max_length=100, 
		help_text=_('A descriptive title helps buyers find your item. <br> State exactly what your post is.'),
	)
	description = RichTextField(
		_('Description'), 
		help_text=_('Describe the your post and provide complete and accurate details. Use a clear and concise format.')
	)

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.title)
		self.title = capfirst(self.title)
		super().save(*args, **kwargs)

	class Meta:
		abstract = True


class ItemListing(ListingPost):
	USED = 'U'
	NEW = 'N'
	DEFECTIVE = 'D'

	CONDITIONS = (
		(NEW, _('New')),  # maybe not packaged but not yet used or fairly used (still new)
		(USED, _('Used')),  # already used but still working
		(DEFECTIVE, _('Defective(some parts are not working)'))  # for parts or not working
	)

	# delete listing if user is deleted
	poster = models.ForeignKey(
		User, 
		on_delete=models.CASCADE,
		related_name='item_listings',
		related_query_name='item_listing'
	)
	city = models.ForeignKey(
		City,
		verbose_name=_('City'),
		on_delete=models.CASCADE,
		related_name='item_listings',
		related_query_name='item_listing'
	)
	sub_category = models.ForeignKey(
		ItemSubCategory, 
		verbose_name=_('Sub category'),
		related_name='item_listings', 
		related_query_name='item_listing',
		on_delete=models.RESTRICT
	)
	condition = models.CharField(
		_('Condition'),
		max_length=3,
		choices=CONDITIONS,
		default=NEW,
		help_text=_("Select the condition of the item you're listing.")
	)
	condition_description = models.TextField(
		_('Condition description'),
		help_text=_('Provide details about the condition of a non brand-new item, including any defects or flaws, so that buyers know exactly what to expect.'),
		blank=True,
		max_length=MAX_TEXT_LENGTH
	)
	# in form, field will be displayed as charfield. this is to enable entering of spaces..
	price = models.PositiveIntegerField(
		_('Price'), 
		help_text=_("Figures and spaces only, no commas or dots. <br> Enter <b>0</b> for free products or services."),
	)
	bookmarkers = models.ManyToManyField(
		User,
		through='ItemListingBookmark',
		related_name='bookmarked_item_listings',
		related_query_name='bookmarked_item_listing',
		blank=True
	)

	def get_absolute_url(self, with_slug=True):
		""" Returns the url to access a detail record for this item. """
		if with_slug:
			return reverse('marketplace:item-listing-detail', kwargs={'pk': self.id, 'slug': self.slug})
		return reverse('marketplace:item-listing-detail', kwargs={'pk': self.id})

	class Meta:
		verbose_name_plural = 'Item Listings'
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime'])
		]


class ItemListingBookmark(models.Model):
	item_listing = models.ForeignKey(
		ItemListing,
		on_delete=models.CASCADE,
		related_name='+'
	)
	bookmarker = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='+'
	)
	bookmark_datetime = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['item_listing', 'bookmarker'],
				name='unique_item_listing_bookmark'
			),
		]


class AdListing(ListingPost):
	poster = models.ForeignKey(
		User, 
		on_delete=models.CASCADE,
		related_name='ad_listings',
		related_query_name='ad_listing'
	)
	category = models.ForeignKey(
		'AdCategory', 
		verbose_name=_('Category'),
		related_name='ad_listings', 
		related_query_name='ad_listing',
		on_delete=models.RESTRICT
	)
	pricing = models.CharField(
		_('Pricing'), 
		help_text=_("Allow this field empty for free products and services or if the pricing is in the advert description."),
		default='-',
		max_length=40
	)
	city = models.ForeignKey(
		City,
		verbose_name=_('City'),
		on_delete=models.CASCADE,
		related_name='ad_listings',
		related_query_name='ad_listing',
		null=True, blank=True,
		help_text=_('Allow this field empty if this advert does not concern a particular city.')
	)
	bookmarkers = models.ManyToManyField(
		User,
		through='AdListingBookmark',
		related_name='bookmarked_ad_listings',
		related_query_name='bookmarked_ad_listing',
		blank=True
	)

	def get_absolute_url(self, with_slug=True):
		if with_slug:
			return reverse('marketplace:ad-listing-detail', kwargs={'pk': self.id, 'slug': self.slug})
		return reverse('marketplace:ad-listing-detail', kwargs={'pk': self.id})

	class Meta:
		ordering = ['-posted_datetime']
		indexes = [
			models.Index(fields=['-posted_datetime'])
		]


class AdListingBookmark(models.Model):
	ad_listing = models.ForeignKey(
		AdListing,
		on_delete=models.CASCADE,
		related_name='+'
	)
	bookmarker = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='+'
	)
	bookmark_datetime = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['ad_listing', 'bookmarker'],
				name='unique_ad_listing_bookmark'
			),
		]
