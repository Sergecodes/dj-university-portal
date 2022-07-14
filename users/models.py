from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import validate_email
from django.db import models
from django.db.models import F
from django.utils import timezone
from django.utils.translation import get_language, gettext_lazy as _

from core.constants import (
	GENDERS, DELETED_USER_EMAIL, REQUIRED_DOWNVOTE_POINTS,
	MAX_ANSWERS_PER_USER_PER_QUESTION, POST_DOWNVOTE_POINTS_CHANGE,
	ANSWER_SCHOOL_QUESTION_POINTS_CHANGE, ANSWER_ACADEMIC_QUESTION_POINTS_CHANGE,
	THRESHOLD_POINTS, INITIAL_POINTS, RESTRICTED_POINTS, COMMENT_CAN_EDIT_UPVOTE_LIMIT,
	MAX_ANSWERS_PER_USER_PER_QUESTION, QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT,
	QUESTION_CAN_EDIT_VOTE_LIMIT, ANSWER_CAN_EDIT_VOTE_LIMIT,
	QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT, QUESTION_CAN_DELETE_VOTE_LIMIT, 
	ANSWER_CAN_DELETE_VOTE_LIMIT, COMMENT_CAN_DELETE_UPVOTE_LIMIT
)
from core.model_fields import NormalizedEmailField
from core.utils import parse_phone_number, translate_text
from core.validators import FullNameValidator, UsernameValidator
from flagging.models import Flag
from notifications.models import Notification
from notifications.signals import notify
from .managers import (
	UserManager, ModeratorManager, 
	StaffManager, ActiveUserManager
)

User = settings.AUTH_USER_MODEL


def get_dummy_user():
	"""
	Dummy user to use as owner of posts that belong to deleted users.
	Normally, users accounts should note be deletable, but can be deactivated(set is_active=False)
	"""
	password = 'deleted-user-password'

	return User.objects.get_or_create(
		username='deleted',
		email=DELETED_USER_EMAIL,
		defaults={
			'password': password, 
			'is_active': False,
			'full_name': 'Deleted User'
		}
	)[0]


class PhoneNumber(models.Model):
	# don't add any `datetime_added` field coz when user edits profile, 
	# all his phone numbers are removed and his phone numbers are recreated.
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
		User, 
		on_delete=models.CASCADE,
		related_name='phone_numbers',
		related_query_name='phone_number'
	)

	def __str__(self):
		if self.can_whatsapp:
			return f"{parse_phone_number(self.number)}, {self.operator}, {_('Supports WhatsApp')}"
		return f"{parse_phone_number(self.number)}, {self.operator}, {_('No WhatsApp')}"

	class Meta:
		verbose_name = _("Phone Number")
		verbose_name_plural = _("Phone Numbers")


class User(AbstractBaseUser, PermissionsMixin):
	email = NormalizedEmailField(
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
		help_text=_(
			'Your username should be between 4 to 15 characters '
			'and the first 4 characters must be letters. <br> '
			'It should not contain any symbols, dashes or spaces. <br>'
			'All other characters are allowed (letters, numbers, hyphens and underscores).'
		),
		error_messages={
			'unique': _('A user with that username already exists.'),
		},
		validators=[UsernameValidator()]
	)
	full_name = models.CharField(
		_('Full name'),
		max_length=25,
		help_text=_(
			'Enter a valid full name. It should be two or three of your names separated by a space ' 
			'and each name may contain only letters or hyphens. <br>'
			'No name should start or end with a hyphen, and no name should contain only hyphens.'
		),
		validators=[FullNameValidator()]
	)
	first_language = models.CharField(
		_('First language'),
		choices=settings.LANGUAGES,
		default='en',
		max_length=3,
		help_text=_(
			"Your preferred language. Don't worry, you can always view the site in another language."
		)
	)
	gender = models.CharField(
		_('Gender'),
		choices=GENDERS,
		default='M',
		max_length=2,
	)

	# +10 points for joining the site lol
	# this amount is also to account for sudden downvotes so that downvoted user's points
	# don't suddenly reach say 0.
	site_points = models.PositiveIntegerField(
		_('Site points'), 
		default=INITIAL_POINTS, 
		editable=False
	)  

	deactivation_datetime = models.DateTimeField(
		_('Deactivation date/time'), 
		null=True, blank=True, 
		editable=False
	)
	datetime_joined = models.DateTimeField(_('Date/time joined'), auto_now_add=True)
	is_superuser = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)   # worker in company(staff)
	is_mod = models.BooleanField(default=False)   # site moderator
	# can login ? set to False by default since user has to confirm email address...
	is_active = models.BooleanField(default=False)  


	USERNAME_FIELD = 'email'
	# USERNAME_FIELD and password are required by default
	REQUIRED_FIELDS = ['username', 'full_name']   

	objects = UserManager()
	active = ActiveUserManager()
	moderators = ModeratorManager()
	staff = StaffManager()

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
			# print("User's account deactivated successfully")
	
	def get_absolute_url(self):
		if self.has_social_profile:
			return self.social_profile.get_absolute_url()
		return ''

	def absolve_post(self, post):
		"""Remove all flags from a post"""
		if self.is_mod:
			flag = Flag.objects.get_flag(post)
			# don't use bulk_delete so that signals are triggered
			for flag_instance in flag.flags():
				flag_instance.delete()

			return True
			
		return False

	def get_earnings(self):
		"""Get user's earnings from his points"""
		# for now, return 0   # TODO
		return 0

	## QA_SITE APP
	def add_answer(self, question, new_answer, question_type):
		"""Add answer to question."""
		# question_type can be 'academic' or 'school-based'
		# note that answer hasn't yet been saved, it's just an Answer() instance.
		# this must be the case coz the answer doesn't yet have a question.

		question_poster = question.poster
		
		answerers_id = []
		# don't use the same 'answer' parameter in this loop.
		# for loop scope..
		for answer in question.answers.all():
			answerers_id.append(answer.poster_id)

		# if user has already exceeded limit for number of answers to this question
		# do not add answer
		if answerers_id.count(self.id) == MAX_ANSWERS_PER_USER_PER_QUESTION:
			return (
				False, 
				_("You can have at most {} answers per question.").format(
					MAX_ANSWERS_PER_USER_PER_QUESTION
				)
			)

		current_lang = get_language()

		## TRANSLATION
		if settings.ENABLE_GOOGLE_TRANSLATE:
			# get language to translate to
			trans_lang = 'fr' if current_lang == 'en' else 'en'
			translated_content = translate_text(new_answer.content, trans_lang)['translatedText']
			setattr(new_answer, f'content_{trans_lang}', translated_content)

		new_answer.poster = self
		new_answer.question = question
		new_answer.original_language = current_lang
		new_answer.save()

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
			target=question,
			category=Notification.ACTIVITY
		)
		for follower in question.followers.all():
			notify.send(
				sender=self, 
				recipient=follower, 
				verb=_('performed an activity under the question'),
				target=question,
				category=Notification.FOLLOWING
			)

		return (True, '')

	def add_question_comment(self, question, new_comment):
		"""Add comment to question."""
		# question_type can be 'academic' or 'school-based'
		# note that comment hasn't yet been saved, it's just an Comment() instance.
		# this must be the case coz the comment doesn't yet have a question.
		new_comment.poster = self
		new_comment.question = question
		new_comment.original_language = get_language()
		new_comment.save()

		# notify question poster and users that are following this question
		notify.send(
			sender=self, 
			recipient=question.poster, 
			verb=_('commented on your question'),
			target=question,
			category=Notification.ACTIVITY
		)
		for follower in question.followers.all():
			notify.send(
				sender=self,
				recipient=follower, 
				verb=_('performed an activity under the question'),
				target=question,
				category=Notification.FOLLOWING
			)
	
	def add_answer_comment(self, answer, new_comment):
		"""Add comment to answer."""
		# note that comment hasn't yet been saved, it's just an Comment() instance.
		# this must be the case coz the comment doesn't yet have a question.
		new_comment.poster = self
		new_comment.answer = answer
		new_comment.original_language = get_language()
		new_comment.save()

		question = answer.question

		# notify question poster, answerer and users that are following this question
		notify.send(
			sender=self, 
			recipient=question.poster, 
			verb=_('commented on an answer to your question'),
			target=question,
			category=Notification.ACTIVITY
		)
		notify.send(
			sender=self, 
			recipient=answer.poster, 
			verb=_('commented on your answer to the question'),
			target=question,
			category=Notification.ACTIVITY
		)
		
		question_followers = question.followers.all()
		for follower in question_followers:
			notify.send(
				sender=self, 
				recipient=follower, 
				verb=_('performed an activity under an answer to the question'),
				target=question,
				category=Notification.FOLLOWING
			)	

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

		# see core/constants.py file; comment under `RESTRICTED_POINTS` for explanation.
		owner_points = question_owner.site_points
		if owner_points == RESTRICTED_POINTS:
			owner_points = RESTRICTED_POINTS + 1
			# first update database so as to flawlessly leverage F expressions
			question_owner.save(update_fields=['site_points'])

		# penalise question owner for downvote
		new_points = F('site_points') + POST_DOWNVOTE_POINTS_CHANGE
		if new_points < THRESHOLD_POINTS:
			new_points = THRESHOLD_POINTS

		question_owner.site_points = new_points
		question_owner.save(update_fields=['site_points'])
		question.downvoters.add(self)
		return (True, question.downvote_count) if output else (True, '')

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

		# see core/constants.py file; comment under `RESTRICTED_POINTS` for explanation.
		owner_points = answer_owner.site_points
		if owner_points == RESTRICTED_POINTS:
			owner_points = RESTRICTED_POINTS + 1
			# first update database so as to flawlessly leverage F expressions
			answer_owner.save(update_fields=['site_points'])

		# penalise question owner for downvote
		new_points = F('site_points') + POST_DOWNVOTE_POINTS_CHANGE
		if new_points < THRESHOLD_POINTS:
			new_points = THRESHOLD_POINTS

		answer_owner.site_points = new_points
		answer_owner.save(update_fields=['site_points'])
		answer.downvoters.add(self)
		return (True, answer.downvote_count) if output else (True, '')

	# Verify if user can edit or delete posts ##
	# NOTE that if any argument is added to any of these functions,
	# some functionalities will break, including the template filters in core/template_tags module.
	def can_edit_question(self, question):
		"""
		Verify if user is permitted to edit question
		
		To test if a user can edit a question.
		- Questions with (3 score or 2 answers) and above can't be edited
		- Only poster can edit question
		"""
		
		# first verify if answer can be edited
		if question.score > QUESTION_CAN_EDIT_VOTE_LIMIT or \
			question.num_answers > QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT:
			return False

		# now verify if user is poster
		if self.id == question.poster_id:
			return True

		return False

	def can_delete_question(self, question):
		"""
		To test if a user can delete a question.
		- Staff can delete any question(any post)
		- Moderator can delete only flagged questions(posts)
		- Poster can delete question only if it has less than 3 votes or less than 2 answers
		"""
		
		if self.is_staff:
			return True

		# if listing is flagged moderator can delete it.
		# first verify if question is flagged before verifying number of answers...
		# coz there could be cases where a question has say 2 "bizarre" answers.. and it could be flagged
		# so if it is flagged, moderator can delete.
		if self.is_mod and Flag.objects.is_flagged(question):
			return True
		
		# verify if question can be deleted
		if question.score > QUESTION_CAN_DELETE_VOTE_LIMIT or \
			question.num_answers > QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT:
			return False

		# now verify if user is owner
		if self.id == question.poster_id:
			return True
		
		return False

	def can_edit_answer(self, answer):
		"""
		To test if a user can edit an answer.
		- Answers with (5 score) and above can't be edited
		- Only poster can edit answer
		"""
					
		# first verify if answer can be edited
		if answer.score > ANSWER_CAN_EDIT_VOTE_LIMIT:
			return False

		# now verify if user is poster
		if self.id == answer.poster_id:
			return True

		return False

	def can_delete_answer(self, answer):
		"""
		To test if a user can delete an answer.
		- Staff can delete any answer
		- Moderator can delete only flagged answers
		- Poster can delete answer only if it has less than 3 votes
		"""
					
		if self.is_staff:
			return True
		
		# if it is flagged, moderator can delete.
		if self.is_mod and Flag.objects.is_flagged(answer):
			return True

		# verify if answer can be deleteed
		if answer.score > ANSWER_CAN_DELETE_VOTE_LIMIT:
			return False

		# now verify if user is poster
		if self.id == answer.poster_id:
			return True

		return False

	def can_edit_comment(self, comment):
		"""
		To test if a user can edit an comment.
		- Only poster can edit comment
		- After 5 minutes, comments can't be edited.
		- Comments with 5 upvotes and above can't be edited
		"""
					
		# first verify if comment can be edited
		if (comment.upvote_count > COMMENT_CAN_EDIT_UPVOTE_LIMIT) or \
			not comment.is_within_edit_timeframe:
			return False

		# now verify if user is poster
		if self.id == comment.poster_id:
			return True

		return False

	def can_delete_comment(self, comment):
		"""
		To test if a user can delete a comment.
		- Staff can delete any comment
		- Moderator can delete only flagged comments
		- Comments with 5 upvotes and above can't be deleted by mod nor poster.
		- Poster can delete comment
		"""
					
		if self.is_staff:
			return True

		# if it is flagged, moderator can delete.
		if self.is_mod and Flag.objects.is_flagged(comment):
			return True

		# verify if comment can be deleted
		if comment.upvote_count > COMMENT_CAN_DELETE_UPVOTE_LIMIT:
			return False

		# now verify if user is poster
		if self.id == comment.poster_id:
			return True

		return False

	## PAST PAPERS APP
	# RECALL that past papers shouldn't be editable.

	def can_delete_past_paper(self, past_paper):
		"""
		To test if user can delete past paper(in this order)
		- Staff can delete any paper
		- Moderator can delete only flagged papers(despite of the posted datetime)
		- After 30mins, past paper can't be deleted by poster
		- Poster can delete paper
		"""
					
		if self.is_staff:
			return True

		# if it is flagged, moderator can delete.
		if self.is_mod and Flag.objects.is_flagged(past_paper):
			return True
		
		if not past_paper.is_within_delete_timeframe:
			return False
			
		if self.id == past_paper.poster_id:
			return True

		return False

	def can_edit_past_paper_comment(self, comment):
		"""
		To test if user can edit past paper comment
		- After 10mins, comment can't be edited
		- Only poster can edit comment
		"""
					
		# is comment editable ?
		if not comment.is_within_edit_timeframe:
			return False

		# now verify if user is poster
		if self.id == comment.poster_id:
			return True
			
		return False

	def can_delete_past_paper_comment(self, comment):
		"""
		To test if user can delete past paper comment
		- staff can delete any comment
		- moderators can delete flagged comments
		- After 10mins, comment can't be deleted by poster
		- poster can delete comment; other users nope.
		"""
					
		if self.is_staff:
			return True

		# if it is flagged, moderator can delete.
		if self.is_mod and Flag.objects.is_flagged(comment):
			return True
		
		if not comment.is_within_delete_timeframe:
			return False
			
		if self.id == comment.poster_id:
			return True

		return False



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
