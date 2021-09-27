import uuid
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
# from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
# from django.contrib.contenttypes.models import ContentType
from django.core.validators import validate_email
from django.db import models
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from notifications.signals import notify

from core.constants import (
	DELETED_USER_EMAIL, REQUIRED_DOWNVOTE_POINTS, PENALIZE_FLAGGED_USER_POINTS_CHANGE,
	MAX_ANSWERS_PER_USER_PER_QUESTION, POST_DOWNVOTE_POINTS_CHANGE, IS_BAD_USER_POINTS,
	ANSWER_SCHOOL_QUESTION_POINTS_CHANGE, ANSWER_ACADEMIC_QUESTION_POINTS_CHANGE
)
from core.model_fields import LowerCaseEmailField, TitleCaseField
from core.utils import parse_phone_number
from marketplace.models import ItemListing, AdListing
# from qa_site.models import AcademicQuestion, SchoolQuestion
from .managers import UserManager
from .validators import validate_full_name


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

	def __str__(self):
		if self.can_whatsapp:
			return f"{parse_phone_number(self.number)}, {self.operator}, {_('Supports WhatsApp')}"
		return f"{parse_phone_number(self.number)}, {self.operator}, {_('No WhatsApp')}"

	class Meta:
		# unique_together = ("content_type", "object_id")
		verbose_name = _("Phone Number")
		verbose_name_plural = _("Phone Numbers")


class User(AbstractBaseUser, PermissionsMixin):
	GENDERS = (
		('M', _('Male')),
		('F', _('Female'))
	)

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

	# +5 points for joining the site lol
	site_points = models.PositiveIntegerField(_('Site points'), default=5, editable=False)  

	# determine if users profile page is visible to other users
	# is_visible = models.BooleanField(
	# 	_('Profile visible to other users'),
	# 	default=False, 
	# 	help_text=_("Enable other users to be able to view your profile. <br>This means they will be able to see information such as your phone numbers.")
	# )
	deactivation_datetime = models.DateTimeField(_('Deactivation date/time'), null=True, blank=True, editable=False)
	datetime_joined = models.DateTimeField(_('Date/time joined'), auto_now_add=True)
	last_login = models.DateTimeField(_('Last login'), auto_now=True)
	is_superuser = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)   # worker in company(staff)
	is_mod = models.BooleanField(default=False)   # site moderator
	is_active = models.BooleanField(default=True)   # can login ?

	USERNAME_FIELD = 'email'
	# USERNAME_FIELD and password are required by default
	REQUIRED_FIELDS = ['username', 'full_name']   

	objects = UserManager()

	class Meta:
		indexes = [
			models.Index(fields=['-site_points'])
		]
	

	def __str__(self):
		return f'{self.username}, {self.full_name}'

	@property
	def can_withdraw(self):
		return False # for now... TODO !

	@property
	def has_social_profile(self):
		"""Determines whether user has activated a social profile(Socialize account)"""
		if hasattr(self, 'social_profile'):
			return True
		return False

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
		self.deactivation_datetime = timezone.now()
		self.is_active = False
		self.save(update_fields=['is_active', 'deactivation_datetime'])

	def delete(self, *args, **kwargs):
		really_delete = kwargs.pop('really_delete', False)

		if really_delete:
			return super().delete(*args, **kwargs) 
		else:
			self.deactivate()
			print("User's account deactivated successfully")
	
	def get_absolute_url(self):
		if self.has_social_profile:
			return self.social_profile.get_absolute_url()
		return ''

	def penalize_flagged_user(self, flagged_post=None):
		"""
		Deduct points from flagged user
		i.e. user whose post flag count attains `SHOULD_FLAG_COUNT` or whose post was deleted by
		moderator for inappropriateness.
		"""
		user_points = self.site_points

		# is user was recently flagged (if he was flagged but didn't contribute to the site)
		# i.e if his points == IS_BAD_USER_POINTS(1)
		# deactivate his account. 
		if user_points == IS_BAD_USER_POINTS:
			# TODO include this in list of website rules.
			self.deactivate()
			return
		
		# if new points after deduction will be less than 1, set it to 1.
		new_points = user_points + PENALIZE_FLAGGED_USER_POINTS_CHANGE
		if new_points < IS_BAD_USER_POINTS:
			new_points = IS_BAD_USER_POINTS

		self.site_points = new_points
		self.save(update_fields=['site_points'])
		# notify user
		notify.send(
			sender=self,  # just use same user as sender
			recipient=self, 
			verb=_(
				"You have been deducted {} points because many users considered one of your posts to be inappropriate. Strive to avoid posting such posts. If you continue, your account will be deactivated without further warning.".format(abs(PENALIZE_FLAGGED_USER_POINTS_CHANGE))
			),
			target=flagged_post
		)

	def get_earnings(self):
		"""Get user's earnings from his points"""
		# for now, return the user's points.  # TODO
		return self.site_points

	def add_answer(self, question, answer, question_type):
		"""Add answer to question."""
		# question_type can be 'academic' or 'school-based'
		# note that answer hasn't yet been saved, it's just an Answer() instance.
		# this must be the case coz the answer doesn't yet have a question.

		question_poster = question.poster
		
		answerers_id = []
		for answer in question.answers:
			answerers_id.append(answer.poster_id)

		# if user has already exceeded limit for number of answers to this question
		# do not add answer
		if answerers_id.count(self.id) == MAX_ANSWERS_PER_USER_PER_QUESTION:
			return (
				False, 
				_("You can have at most {} answers per question.").format(MAX_ANSWERS_PER_USER_PER_QUESTION)
			)

		answer.poster = self
		answer.question = question
		answer.save()

		# update user's number of points if answerer is not question poster
		if question_poster != self:
			if question_type == 'school-based':
				self.site_points = F('site_points') + ANSWER_SCHOOL_QUESTION_POINTS_CHANGE
			elif question_type == 'academic':
				self.site_points = F('site_points') + ANSWER_ACADEMIC_QUESTION_POINTS_CHANGE
			else:
				raise ValueError(f"Invalid value for question_type. Value can be either 'academic' or 'school-based' not '{question_type}'.")
			self.save(update_fields=['site_points'])

		# notify question owner and users that are following this question
		notify.send(
			sender=self, 
			recipient=question_poster, 
			verb=_('answered your question'),
			target=question
		)
		for follower in question.followers.all():
			notify.send(
				sender=self, 
				recipient=follower, 
				verb=_('performed an activity under the question'),
				target=question
			)

		return (True, '')

	def add_question_comment(self, question, comment):
		"""Add comment to question."""
		# question_type can be 'academic' or 'school-based'
		# note that comment hasn't yet been saved, it's just an Comment() instance.
		# this must be the case coz the comment doesn't yet have a question.
		comment.poster = self
		comment.question = question
		comment.save()

		# notify question poster and users that are following this question
		notify.send(
			sender=self, 
			recipient=question.poster, 
			verb=_('commented on your question'),
			target=question
		)
		for follower in question.followers.all():
			notify.send(
				sender=self,
				recipient=follower, 
				verb=_('performed an activity under the question'),
				target=question
			)
	
	def add_answer_comment(self, answer, comment):
		"""Add comment to answer."""
		# note that comment hasn't yet been saved, it's just an Comment() instance.
		# this must be the case coz the comment doesn't yet have a question.
		comment.poster = self
		comment.answer = answer
		comment.save()

		question = answer.question

		# notify question poster, answerer and users that are following this question
		notify.send(
			sender=self, 
			recipient=question.poster, 
			verb=_('commented on an answer to your question'),
			target=question
		)
		notify.send(
			sender=self, 
			recipient=answer.poster, 
			verb=_('commented on your answer to the question'),
			target=question
		)
		
		question_followers = question.followers.all()
		for follower in question_followers:
			notify.send(
				sender=self, 
				recipient=follower, 
				verb=_('performed an activity under an answer to the question'),
				target=question
			)
	
	'''Upvoting/downvoting questions and answers'''
	# def upvote_question(self, question, output=False):
	# 	question.upvoters.add(self)
	# 	return question.upvote_count if output else None

	# def unupvote_question(self, question, output=False):
	# 	question.upvoters.remove(self)
	# 	return question.upvote_count if output else None

	# def upvote_answer(self, answer, output=False):
	# 	answer.upvoters.add(self)
	# 	return answer.upvote_count if output else None

	# def unupvote_answer(self, answer, output=False):
	# 	answer.upvoters.remove(self)
	# 	return answer.upvote_count if output else None	

	
	def downvote_question(self, question, output=False, for_html=False):
		question_owner = question.poster

		# user can't downvote(vote for his own question(post))
		if self == question_owner:
			return (
				False,
				_("You can't add a dislike to your own question.")
			)

		# staff can always downvote question
		if not self.is_staff:
			# user should have enough points to downvote
			if for_html:
				# boldface the required number of points.
				return (
					False, 
					_("You need at least <strong>{} points</strong> to be able to add a dislike.").format(REQUIRED_DOWNVOTE_POINTS)
				)

			return (
				False, 
				_("You need at least {} points to be able to add a dislike.").format(REQUIRED_DOWNVOTE_POINTS)
			)

		question_owner.site_points = F('site_points') + POST_DOWNVOTE_POINTS_CHANGE
		question.downvoters.add(self)
		return (True, question.downvote_count) if output else (True, '')

	# def undownvote_question(self, question, output=False):
	# 	question.downvoters.remove(self)
	# 	return question.downvote_count if output else None

	def downvote_answer(self, answer, output=False, for_html=False):
		answer_owner = answer.poster

		# user can't downvote(vote for his own answer(post))
		if self == answer_owner:
			return (
				False,
				_("You can't add a dislike to your own answer.")
			)

		# staff can always downvote answer
		if not self.is_staff:
			# user doesn't have enough points to downvote
			if self.site_points < REQUIRED_DOWNVOTE_POINTS:
				if for_html:
					return (
						False, 
						_("You need at least <strong>{} points</strong> to be able to add a dislike.").format(REQUIRED_DOWNVOTE_POINTS)
					)

				return (
					False, 
					_("You need at least {} points to be able to add a dislike.").format(REQUIRED_DOWNVOTE_POINTS)
				)

		answer.downvoters.add(self)
		return (True, answer.downvote_count) if output else (True, '')

	# def undownvote_answer(self, answer, output=False):
	# 	answer.downvoters.remove(self)
	# 	return answer.downvote_count if output else None	

	# def bookmark_question(self, question, output=False):
	# 	question.bookmarkers.add(self)
	# 	return question.bookmark_count if output else None

	# def unbookmark_question(self, question, output=False):
	# 	question.bookmarkers.remove(self)
	# 	return question.bookmark_count if output else None

	# def bookmark_listing(self, listing, output=False):
	# 	listing.bookmarkers.add(self)
	# 	return listing.bookmark_count if output else None

	# def unbookmark_listing(self, listing, output=False):
	# 	listing.bookmarkers.remove(self)
	# 	return listing.bookmark_count if output else None



# this model isn't even required. if user flaunts a law, he will be warned.
# if he persists, his account will be deleted(deactivated.)
# class Suspension(models.Model):
# 	# Moderators should suspend users if they are constantly reported, after warning etc
# 	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
# 	creation_datetime = models.DateTimeField(auto_now_add=True)
# 	duration = models.DurationField(default=timedelta(days=1))  # default suspension period
# 	is_active = models.BooleanField(default=True)
# 	reason = models.TextField()
# 	user = models.ForeignKey(
# 		User,
# 		on_delete=models.CASCADE,
# 		related_name='suspensions',
# 		related_query_name='suspension'
# 	)

# 	@property
# 	def ending_datetime(self):
# 		""" When the suspension will end """
# 		return self.creation_datetime + self.duration



# import uuid

# from django.contrib.auth import get_user_model
# # from django.core.cache import caches

# User = get_user_model()
# # DEFAULT_IMAGE_URL = 'imgur.co'
# DELETED_USER_EMAIL = 'deleted@gmail.com'

# # TODO this accounts should proly be created before deployment...

# def get_sentinel_user():
# 	"""
# 	A dummy profile that will be used for deleted profiles.
# 	However, deleted profiles are not purged out of the db.
# 	In case a user is deleted, set his profile to the dummy profile
# 	and set him to inactive. Don't actually delete the user!
# 	"""
# 	# store this user in cache
# 	password = str(uuid.uuid4())
# 	return User.objects.get_or_create(
# 		username='deleted',
# 		email=DELETED_USER_EMAIL,  # irrelevant dummy email
# 		defaults={'password': password, 'is_active': False}
# 	)[0]   # get_or_create() returns (obj, created?). so [0] return just the object.

