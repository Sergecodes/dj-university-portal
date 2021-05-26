import uuid
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.model_fields import LowerCaseEmailField, TitleCaseField
from core.validators import validate_full_name
from marketplace.models import MarketplaceProfile
from .managers import UserManager

# dating
# 	- social media account (-facebook link, twitter link)
# 	- tel number
# qa_site
# 	-
# marketplace:
# 	- tel number
# 	- full name
# common:
# 	email, username(display name), full_name


class User(AbstractBaseUser, PermissionsMixin):
	# TODO deletion from one site => deletion from whole site. same as suspension.
	# User should see all his info in one page (like one profile).
	ACTIVE = 'A'
	DELETED = 'D'
	SUSPENDED = 'S'

	STATUSES = (
		(ACTIVE, 'active'),
		(DELETED, 'deleted'),
		(SUSPENDED, 'suspended')
	)

	email = LowerCaseEmailField(
		_('Email address'),
		max_length=50,
		unique=True,
		help_text=_('We will send a verification code to this email'),
		error_messages={
			'unique': _('A user with that email already exists'),
			# null, blank, invalid, invalid_choice, unique, unique_for_date
		},
	)
	username = models.CharField(
		_('Username'),
		max_length=15,
		unique=True,
		help_text=_('This is the name people will know you by on this site. You can always change it later'),
		error_messages={
			'unique': _('A user with that username already exists'),
		},
	)
	full_name = TitleCaseField(
		_('Full name'),
		max_length=25,
		help_text=_('Two of your names will be okay. Please enter your real names.'),
		blank=True,  # no null=True needed for char and text fields. default for blank & null is False.
		# if no value is set and the field is nullable, the value is stored in the database as an empty string ('')
		validators=[validate_full_name]
	)
	status = models.CharField(choices=STATUSES, default='A', max_length=2)
	first_language = models.CharField(
		_('First language'),
		choices=settings.LANGUAGES,
		default='en',
		max_length=3,
		help_text=_('Your preferred language')
	)
	deletion_datetime = models.DateTimeField(_('Deletion date/time'), null=True, blank=True)
	datetime_joined = models.DateTimeField(_('Date/time joined'), default=timezone.now)
	last_login = models.DateTimeField(_('Last login'), auto_now=True)
	is_superuser = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)   # worker in company(staff)
	is_mod = models.BooleanField(default=False)   # site moderator
	is_active = models.BooleanField(default=True)   # can login ?

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username', 'full_name']   # USERNAME_FIELD and password are required by default

	objects = UserManager()

	def get_full_name(self):
		return self.full_name

	def __str__(self):
		return f'{self.full_name}'

	def delete(self):
		# Don't actually delete user account, just do this instead
		self.status = 'D'
		self.deletion_datetime = timezone.now()
		self.is_active = False
		self.save(update_fields=['is_active', 'status', 'deletion_datetime'])

	@property
	def current_suspension(self):
		active_suspension = self.suspensions.filter(is_active=True)
		# ensure that either 0 or 1 suspension can be active.
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


class Suspension(models.Model):
	# Moderators should suspend users if they are constantly reported, after warning etc
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	creation_datetime = models.DateTimeField(auto_now_add=True)
	duration = models.DurationField(default=timedelta(days=1))  # default suspension period
	is_active = models.BooleanField(default=True)
	reason = models.TextField()
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='suspensions',
		related_query_name='suspension'
	)

	@property
	def ending_datetime(self):
		""" When the suspension will end """
		return self.creation_datetime + self.duration


@receiver(post_save, sender=get_user_model())
def create_marketplace_profile(sender, instance, created, **kwargs):
	""" When user is created, instantly link to marketplace profile """
	# TODO Do same with qa-site app.
	# instance is a user
	if created:  # if a new user was created
		profile = MarketplaceProfile(user=instance)
		profile.save()
	else:
		# TODO remove this print statement. Infact, this print statement should never be shown (under normal circums..
		print('Unexpectedly, marketplace profile not created.')


# how do you do this in db: "you have 10 votes left for today? "
# TODO nb: Entities: user, Date; Relation: Activity..(num_of_votes, ...)
'''
class User:
	activity_dates = models.ManyToManyField(
		'ActivityDate', 
		through='UserActivity', 
		related_name='+'  # disable mapping reverse relation (from ActivityDate to User). 
		# so no way to do activity_date.user etc.  no need to do this right
	)

	def add_vote(self):
		...
		self.dates.latest
	...

class ActivityDate(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)

class UserActivity(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	activity_date = models.ForeignKey(Date, on_delete=models.CASCADE)

	# Relation fields:
	num_of_votes_left = models.PositiveIntegerField(default=10)


	class Meta:
		# order_with_respect_to = 'activity_date'
		unique_together = [
			('user', 'activity_date'), 
		]
	# then a cron job to remove all entries with date < current date
	# from django.utils.timezone import localtime, now
	remove all entries where entry.datetime.date() < timezone.now().date
'''

# Sentinel user/profile stuff (if user has to be really deleted from db)

# DELETED_USER_EMAIL = 'deleted@gmail.com'
# def get_sentinel_profile():
# 	"""
# 	A dummy profile that will be used for deleted profiles.
# 	However, deleted profiles are not purged out of the db.
# 	:return: sentinel profile
# 	"""
# 	# store this profile in cache.
# 	password = str(uuid.uuid4())  # at least the password should not be guessable!
# 	sentinel_user = User.objects.get_or_create(
# 		username='deleted',
# 		email=DELETED_USER_EMAIL,  # fraudulent irrelevant email
# 		defaults={'password': password, 'is_active': False}
# 	)[0]  # get_or_create() returns (obj, created?). so [0] return just the object.
#
# 	return sentinel_user.profile  # remember, when a user is created, a profile is also created for him
# def get_sentinel_user():
# 	"""
# 	In case a user is deleted, set his profile to the dummy profile
# 	and set him to inactive. Don't actually delete the user!
# 	"""
# 	# store this user in cache
# 	password = str(uuid.uuid4())
# 	return User.objects.get_or_create(
# 		username='deleted',
# 		email=DELETED_USER_EMAIL,  # fraudulent irrelevant email
# 		defaults={'password': password, 'is_active': False}
# 	)[0]

