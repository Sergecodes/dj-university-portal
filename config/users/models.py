import uuid
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import validate_email
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from core.model_fields import LowerCaseEmailField, TitleCaseField
from marketplace.models import ItemListing, AdListing
from .managers import UserManager
from .utils import parse_phone_number
from .validators import validate_full_name


class PhoneNumber(models.Model):
	# don't add any `datetime_added` field coz when user edits profile, all his phone numbers are removed and his phone numbers are recreated.
	ISPs = (
		('MTN', 'MTN'),
		('Nexttel', 'Nexttel'),
		('Orange', 'Orange'),
		('CAMTEL', 'CAMTEL'),
		('O', 'Other')  # TODO add other ISPs.
	)

	operator = models.CharField(_('Operator'), choices=ISPs, max_length=8, default='MTN')
	number = models.CharField(
		_('Phone number'),
		max_length=20,  # filler value since CharFields must define a max_length attribute
		help_text=_('Enter mobile number <b>(without +237)</b>')
	)
	can_whatsapp = models.BooleanField(_('Works with WhatsApp'), default=False)
	owner = models.ForeignKey(
		'User', 
		on_delete=models.CASCADE,
		related_name='phone_numbers',
		related_query_name='phone_number'
	)


	# content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	# object_id = models.PositiveIntegerField()
	# content_object = GenericForeignKey('content_type', 'object_id')

	def __str__(self):
		if self.can_whatsapp:
			return f"{parse_phone_number(self.number)}, {self.operator}, {_('Supports WhatsApp')}"
		return f"{parse_phone_number(self.number)}, {self.operator}, {_('No WhatsApp')}"

	class Meta:
		# unique_together = ("content_type", "object_id")
		verbose_name = _("Phone Number")
		verbose_name_plural = _("Phone Numbers")


# class PhoneNumberTarget(models.Model):
# 	"""
# 	This table will be used as a `through` table for generic many to many field.
# 	This is used because a phone number can point to many objects(many listings and a user)
# 	"""
# 	phone_number = models.ForeignKey(PhoneNumber)



class User(AbstractBaseUser, PermissionsMixin):
	# ACTIVE = 'A'
	# DELETED = 'D'
	# SUSPENDED = 'S'

	# STATUSES = (
	# 	(ACTIVE, _('active')),
	# 	(DELETED, _('deleted')),
	# 	(SUSPENDED, _('suspended'))
	# )

	GENDERS = (
		('M', _('Male')),
		('F', _('Female'))
	)

	# phone_numbers = GenericRelation(PhoneNumber, related_query_name='user')
	email = LowerCaseEmailField(
		_('Email address'),
		max_length=50,
		unique=True,
		help_text=_('We will send a verification code to this email'),
		error_messages={
			'unique': _('A user with that email already exists.'),
			# null, blank, invalid, invalid_choice, unique, unique_for_date
		},
		validators=[validate_email]
	)
	username = models.CharField(
		_('Username'),
		max_length=15,
		unique=True,
		help_text=_('This could be your nickname. You can always change it later.'),
		error_messages={
			'unique': _('A user with that username already exists.'),
		},
		validators=[UnicodeUsernameValidator()]
	)
	full_name = TitleCaseField(
		_('Full name'),
		max_length=25,
		help_text=_('Two of your names will be okay. Please enter your real names.'),
		validators=[validate_full_name]
	)
	first_language = models.CharField(
		_('First language'),
		choices=settings.LANGUAGES,
		default='fr',
		max_length=3,
		help_text=_("Your preferred language. Don't worry, you can always view the site in another language.")
	)
	gender = models.CharField(
		_('Gender'),
		choices=GENDERS,
		default='M',
		max_length=2,
	)
	bookmarked_item_listings = models.ManyToManyField(
		ItemListing,
		related_name='bookmarkers',
		related_query_name='bookmarker'
	)
	bookmarked_ad_listings = models.ManyToManyField(
		AdListing,
		related_name='bookmarkers',
		related_query_name='bookmarker'
	)
	
	# site points can be used for one-day-listing, {video call developer(me), site bonuses, rankings  etc}
	site_points = models.PositiveIntegerField(_('Site points'), default=5)  # +5 points for joining the site lol
	# status = models.CharField(choices=STATUSES, default='A', max_length=2)

	# determine if users profile page is visible to other users
	# is_visible = models.BooleanField(
	# 	_('Profile visible to other users'),
	# 	default=False, 
	# 	help_text=_("Enable other users to be able to view your profile. <br>This means they will be able to see information such as your phone numbers.")
	# )
	deactivation_datetime = models.DateTimeField(_('Deactivation date/time'), null=True, blank=True)
	datetime_joined = models.DateTimeField(_('Date/time joined'), default=timezone.now)
	last_login = models.DateTimeField(_('Last login'), auto_now=True)
	is_superuser = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)   # worker in company(staff)
	is_mod = models.BooleanField(default=False)   # site moderator
	is_active = models.BooleanField(default=True)   # can login ?

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username', 'full_name']   # USERNAME_FIELD and password are required by default

	objects = UserManager()

	class Meta:
		indexes = [
			models.Index(fields=['-site_points'])
		]

	def __str__(self):
		return f'{self.username}, {self.full_name}'

	def clean(self, *args, **kwargs):
		# add custom validation here
		super().clean(*args, **kwargs)
	
	def save(self, *args, **kwargs):
		# full_clean() automatically calls clean()
		self.full_clean()
		super().save(*args, **kwargs)

	def deactivate(self):
		"""Mark user as inactive but allow his record in database."""
		# Don't actually delete user account, just do this instead
		self.status = 'D'
		self.deactivation_datetime = timezone.now()
		self.is_active = False
		self.save(update_fields=['is_active', 'status', 'deactivation_datetime'])

	# def delete(self):
	# 	self.deactivate()
	
	def get_absolute_url(self):
		return reverse('users:view-profile', kwargs={'username': self.username})

	def get_earnings(self):
		"""Get user's earnings from his points"""
		# for now, return the user's points.  # todo
		return self.site_points

	@property
	def can_withdraw(self):
		return False # for now... todo!

	@property
	def has_social_profile(self):
		"""Determines whether user has activated a social profile(Socialize account)"""
		if hasattr(self, 'social_profile'):
			return True
		return False

	@property
	def current_suspension(self):
		active_suspension = self.suspensions.filter(is_active=True)
		# ensure that either no or 1 suspension can be active.
		assert (count := active_suspension.count()) == 0 or count == 1, 'There must be 0 or 1 active suspension.'
		return active_suspension

	@property
	def is_suspended(self):
		"""Verify whether or not user is currently suspended"""
		return True if self.current_suspension else False

	@property
	def total_suspensions(self):
		"""
		Gets the total number of suspensions that the user has ever had.
		TODO User is automatically deleted after 5 suspensions ?
		"""
		return self.suspensions.count()


# dummy email
DELETED_USER_EMAIL = 'deleted@gmail.com'

def get_dummy_user():
	"""
	Dummy user to use as owner of posts that belong to deleted users.
	Normally, users accounts should note be deletable, but can be deactivated(set is_active=False)
	"""
	return User.objects.get_or_create(
		username='deleted',
		email=DELETED_USER_EMAIL,
		defaults={
			'password': str(uuid.uuid4()), 
			'is_active': False
		}
	)[0]


class Suspension(models.Model):
	# Moderators should suspend users if they are constantly reported, after warning etc
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	creation_datetime = models.DateTimeField(auto_now_add=True)
	duration = models.DurationField(default=timedelta(days=1))  # default suspension period
	is_active = models.BooleanField(default=True)
	reason = models.TextField()
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='suspensions',
		related_query_name='suspension'
	)

	@property
	def ending_datetime(self):
		""" When the suspension will end """
		return self.creation_datetime + self.duration

