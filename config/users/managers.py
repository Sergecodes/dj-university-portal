from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.db.models import QuerySet, Manager
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.constants import (
	IS_BAD_USER_POINTS, PENALIZE_FLAGGED_USER_POINTS_CHANGE,
)
from core.utils import parse_email, parse_full_name
from notifications.models import Notification
from notifications.signals import notify


class UserQuerySet(QuerySet):
	# Never call delete on User object !

	# def delete(self):
	# 	# self is a queryset containing the profiles to be deleted; Profile.objects.filter(...).delete()
	# 	# get users from self
	# 	# note: we can't do something like this: Entry.objects.update(blog__name='foo') # Won't work!
	# 	# update() only works on the model's fields, not it's related fields.
	# 	get_user_model().objects.filter(id__in=self).update(is_active=False)
	# 	self.update(status='D', deactivation_datetime=timezone.now())

	def delete(self, really_delete=False):
		if really_delete:
			return super().delete()
		else:
			self.deactivate()

	def deactivate(self):
		self.update(is_active=False, deactivation_datetime=timezone.now())


class UserManager(BaseUserManager, Manager):
	def create_user(
			self, 
			email, 
			username, 
			full_name, 
			password, 
			gender, 
			first_language, 
			commit=True, 
			**extra_fields
		):
		""" 
		Create and save a user with the given email, username, password, etc... . 
		"""

		if not email:
			raise ValueError(_('The email must be set'))
		if not username:
			raise ValueError(_('The username must be set'))
		if not password:
			raise ValueError(_('The password must be set'))
		if not full_name:
			raise ValueError(_('The full name must be set'))
		if not gender:
			raise ValueError(_('The gender must be set'))
		if not first_language:
			raise ValueError(_('The first language must be set'))	

		# no need for this, it will be called when the object is been saved.
		# since it is included in the validators property of the username field.
		# validate_username = UsernameValidator()
		# validate_username(username)
		
		user = self.model(
			email=parse_email(email), 
			username=username, 
			full_name=parse_full_name(full_name), 
			gender=gender,
			first_language=first_language,
			**extra_fields
		)
		
		validate_password(password)
		user.set_password(password)

		if commit:
			user.save() 

		return user

	def create_superuser(
			self, 
			email, 
			username, 
			full_name, 
			password, 
			gender, 
			first_language, 
			commit=True,
			**extra_fields
		):
		""" 
		Create and save a SuperUser with the given email, name, full name, password etc... 
		"""

		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_mod', True)
		extra_fields.setdefault('is_superuser', True)
		extra_fields.setdefault('is_active', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError(_('Superuser must have is_staff=True.'))
		if extra_fields.get('is_mod') is not True:
			raise ValueError(_('Superuser must have is_mod=True.'))
		if extra_fields.get('is_superuser') is not True:
			raise ValueError(_('Superuser must have is_superuser=True.'))
		
		return self.create_user(
			email=email, 
			username=username, 
			full_name=full_name, 
			gender=gender,
			password=password,
			first_language=first_language,
			**extra_fields
		)

	def get_queryset(self):
		return UserQuerySet(self.model, using=self._db)

	def penalize_user(self, user, flagged_post):
		"""
		Deduct points from flagged user
		i.e. user whose post flag count attains `IS_FLAGGED_COUNT` or whose post was deleted by
		moderator for inappropriateness.
		"""
		user_points = user.site_points

		# if user was recently flagged (if he was flagged but didn't contribute to the site)
		# in other words, this will happen only if user has already posted a flagged post.
		# if his points == IS_BAD_USER_POINTS(1)
		# deactivate his account. 
		if user_points == IS_BAD_USER_POINTS:
			user.deactivate()
			return
		
		# if new points after deduction will be less than 1, 
		# set it to IS_BAD_USER_POINTS(1).
		new_points = user_points + PENALIZE_FLAGGED_USER_POINTS_CHANGE
		if new_points < 1:
			new_points = IS_BAD_USER_POINTS

		user.site_points = new_points
		user.save(update_fields=['site_points'])

		# if current points == IS_BAD_USER_POINTS, that signifies user is a bad user,
		# notify him telling him that if any of his posts if flagged again
		# his account will be deactivated.  
		# don't tell him that if he contributes positively to the site and regains more points
		# he will be free.
		if user_points == IS_BAD_USER_POINTS:
			notify.send(
				sender=user,  # just use same user as sender
				recipient=user, 
				verb=_(
					"You have been deducted {} points because many users considered your post inappropriate. Avoid posting such posts. If any of your posts is reported again, your account will be deactivated without further notice.".format(abs(PENALIZE_FLAGGED_USER_POINTS_CHANGE))
				),
				target=flagged_post,
				category=Notification.FLAG
			)
		else:
			notify.send(
				sender=user,  # just use same user as sender
				recipient=user, 
				verb=_(
					"You have been deducted {} points because many users considered your post inappropriate. Avoid posting such posts. If you continue, your account could be deactivated.".format(abs(PENALIZE_FLAGGED_USER_POINTS_CHANGE))
				),
				target=flagged_post,
				category=Notification.FLAG
			)

	def notify_new_user(self, user):
		"""
		Send notification to newly signed up user.
		This notification contains a link to the official social profile
		of the CamerSchools account and a page to the website info(how to use..).
		"""

		# notification with link to website info..
		notify.send(
			sender=user,  # just use same user as sender
			recipient=user, 
			verb=_("Click here to view information on how to use this website."),
			follow_url=reverse('core:usage-info'),
			category=Notification.GENERAL
		)

		# notification with link to CamerSchools profile
		# camerschools_account = self.get_site_account()
		notify.send(
			sender=user,  # just use same user as sender
			recipient=user, 
			verb=_("Welcome to CamerSchools. Click here to view our social profile"),
			follow_url=reverse('socialize:camerschools-profile'),
			category=Notification.GENERAL
		)

	def active(self):
		return self.model.objects.filter(is_active=True)

	def deactivated(self):
		return self.model.objects.filter(is_active=False, deactivation_datetime__isnull=False)


class ActiveUserManager(Manager):
	def get_queryset(self):
		return super().get_queryset().filter(is_active=True)


class ModeratorManager(Manager):
	def get_queryset(self):
		return super().get_queryset().filter(is_mod=True)


class StaffManager(Manager):
	def get_queryset(self):
		return super().get_queryset().filter(is_staff=True)

