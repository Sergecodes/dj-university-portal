from ckeditor.fields import RichTextField
from datetime import timedelta
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.validators import validate_tel_number_length
from hitcount.models import HitCount, HitCountMixin


class MarketplaceProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    # TODO reputation is not visible to users, only used internally (maybe trivial advantages;
    #  added when users confirm transaction;  also add credit points). Only a user can see his credit points
    reputation = models.PositiveIntegerField(default=1)
    # credit points can be used for one-day-listing, {video call developer(me), site bonuses etc}
    credit_points = models.PositiveIntegerField(_('Credit points'), default=5)  # +5 points for joining the site lol

    def __str__(self):
        return self.user.full_name


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


class PhoneNumber(models.Model):
    ISPs = (
        ('MTN', 'MTN'),
        ('Nexttel', 'Nexttel'),
        ('Orange', 'Orange'),
        ('CAMTEL', 'CAMTEL'),
        ('O', 'Other')  # TODO add other ISPs.
    )
    # TODO ensure user has at least one mtn or orange number. If not one of his numbers should have whatsapp

    operator = models.CharField(_('Operator'), choices=ISPs, max_length=8, default='MTN')
    number = models.CharField(
        _('Phone number'),
        max_length=9,  # TODO change this to an appropriate value
        help_text=_('Enter mobile number <b>(without +237)</b>'),
        validators=[validate_tel_number_length]
    )
    can_whatsapp = models.BooleanField(_('Works with WhatsApp'), default=False)
    owner = models.ForeignKey(
        'MarketplaceProfile',
        on_delete=models.CASCADE,
        related_name='phone_numbers',
        related_query_name='phone_number'
    )

    def __str__(self):
        return f'{self.number}, {self.operator}'


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
    owner = models.OneToOneField('MarketplaceProfile', on_delete=models.CASCADE)
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
    language = models.CharField(
        _('Language'),
        choices=settings.LANGUAGES,
        default='en',  # in template form, default language should be user's current language or first language
        max_length=3
    )

    def bookmark(self):
        self.bookmarks = models.F('number_of_bookmarks') + 1
        self.save(update_fields=['number_of_bookmarks'])

    def remove_bookmark(self):
        self.bookmarks = models.F('number_of_bookmarks') - 1
        self.save(update_fields=['number_of_bookmarks'])

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
        help_text=_('Provide details about the condition of a non brand new item, including any defects of flaws'
                    ', so that buyers know exactly what to expect.')
    )
    hitcount_generic = GenericRelation(
        HitCount,
        object_id_field='object_id',
        related_query_name='item'
    )
    # to enable getting the items that a user has bookmarked(user.bookmarked_items) and also probably the
    # number of people that have bookmarked a user's item ?
    # TODO owners won't be able to see those who bookmarked their posts, but may see number of bookmarks
    bookmarkers = models.ForeignKey(
        'MarketplaceProfile',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='bookmarked_posts',
        related_query_name='bookmarked_post'
    )

    # TODO Only owner/poster can see number of views

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
        'MarketplaceProfile',
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

# TODO moderator should have his own view of the site; they should be able to see pending reports, etc.
# TIPS:
# scheduling listing
# on items page, give user tip that "if he sees an item he's interested in, he should contact the
# owner if the price if understandable. They may still bargain on an agreeable price"

# make money when user post ads:
# bold title in search results (like ebay) cheapest
# subtitle in listing
# boost up posts(faire remonter) (like jumia) cheaper
# vip (like jumia)

# on post description, user shouldnt put contact details; now web links.
# In fact, remove all weblinks from source b4 adding to db..

#
# categories: video games & consoles, toys & hobbies, sporting goods, musical instruments & gear, jewelry & watches,
# 		health & beauty,dvds & movies, crafts, dolls, computers;electronics/tablets & networking, cell phones & accessories,
# 		books,baby,produits Apple
#
# 		livres, films, jouets;instruments de musique;sport & fitness;bijoux & montres;female clothes, male clothes,
# 		female shoes,male shoes,maisons a louer,studios & chambres a louer;motos & velos;mobiles & smartphones

# this site vs jumia:
# 	- concept of points so as to encourage sellers to signal the site that the item has being bought
# 		- a certain num of points => a certain privilege e.g. be moderator?(nope..), contact developers,...
# 		- item sold => +x points to buyer and + y points to seller (x >y)
# 	- form signed upon item purchase which will serve as a receipt...
# 	- users can only perform transaction in  items in univ, hence more security...
