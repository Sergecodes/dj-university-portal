from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone
from django.utils.translation import get_language, gettext_lazy as _

from core.constants import (
	GENDERS, DELETED_USER_EMAIL, REQUIRED_DOWNVOTE_POINTS,
	POST_DOWNVOTE_POINTS_CHANGE, ANSWER_DOWNVOTE_POINTS_CHANGE,
	THRESHOLD_POINTS, INITIAL_POINTS, RESTRICTED_POINTS, 
	QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT, COMMENT_CAN_EDIT_VOTE_LIMIT,
	QUESTION_CAN_EDIT_VOTE_LIMIT, QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT, 
	QUESTION_CAN_DELETE_VOTE_LIMIT, COMMENT_CAN_DELETE_VOTE_LIMIT
)
from core.fields import NormalizedEmailField
from core.models import Country
from core.utils import parse_phone_number, translate_text
from core.validators import UsernameValidator
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
		}
	)[0]


class PhoneNumber(models.Model):
	# Don't add any `datetime_added` field coz when user edits profile, 
	# all his phone numbers are removed and his phone numbers are recreated.

	number = models.CharField(
		_('Phone number'),
		max_length=20,  # filler value since CharFields must define a max_length attribute
		help_text=_('Enter mobile number')
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
			return f"{parse_phone_number(self.number)}, {_('Supports WhatsApp')}"
		return f"{parse_phone_number(self.number)}, {_('No WhatsApp')}"

	class Meta:
		verbose_name = _("Phone Number")
		verbose_name_plural = _("Phone Numbers")


class User(AbstractUser):
	first_name, last_name, date_joined = None, None, None

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
		validators=[UsernameValidator()],
		## https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/operations
		# /#managing-colations-using-migrations
		#
		## https://stackoverflow.com/questions/18807276/
		# how-to-make-my-postgresql-database-use-a-case-insensitive-colation
		#
		## https://gist.github.com/hleroy/2f3c6b00f284180da10ed9d20bf9240a
		# how to use Django 3.2 CreateCollation and db_collation to implement a 
		# case-insensitive Charfield with Postgres > 1
		#
		## https://www.postgresql.org/docs/current/citext.html
		#
		## https://www.postgresql.org/docs/current/collation.html#COLLATION-NONDETERMINISTIC
		# db_collation='case_insensitive'  # TODO Implement this
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
	country = models.ForeignKey(
		Country, 
		verbose_name=_('Country of residence'),
		on_delete=models.RESTRICT,
		related_name='users',
		related_query_name='user',
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
	REQUIRED_FIELDS = ['username', ]   

	objects = UserManager()
	active = ActiveUserManager()
	moderators = ModeratorManager()
	staff = StaffManager()

	class Meta:
		indexes = [
			models.Index(fields=['-site_points'])
		]
	
	def __str__(self):
		return f'{self.username}'

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

			with transaction.atomic():
				# don't use bulk_delete so that signals are triggered
				for flag_instance in flag.flags():
					flag_instance.delete()

			return True
			
		return False

	def get_earnings(self):
		"""Get user's earnings from his points"""
		# for now, return 0   # TODO
		return 0

	def add_question_comment(self, question, new_comment, parent=None):
		"""Add comment to question."""
		# question_type can be 'academic' or 'discuss'
		# note that comment hasn't yet been saved, it's just an Comment() instance.
		# this must be the case coz the comment doesn't yet have a question.
		current_lang = get_language()
		comment = new_comment

		## TRANSLATION
		if settings.ENABLE_GOOGLE_TRANSLATE:
			# get language to translate to
			trans_lang = 'fr' if current_lang == 'en' else 'en'
			translated_content = translate_text(comment.content, trans_lang)['translatedText']
			setattr(comment, f'content_{trans_lang}', translated_content)

		comment.poster = self
		comment.parent = parent
		comment.question = question
		comment.original_language = current_lang
		comment.save()

		# Notify question poster and users that are following this question
		# if comment is a direct comment on question
		if parent is None:
			notify.send(
				sender=self, 
				recipient=question.poster, 
				verb=_('commented on your question'),
				target=question,
				category=Notification.ACTIVITY
			)
		else:
			# notify question poster, answerer and users that are following this question
			notify.send(
				sender=self, 
				recipient=question.poster, 
				verb=_('replied to a comment on your question'),
				target=question,
				category=Notification.ACTIVITY
			)
			notify.send(
				sender=self, 
				recipient=parent.poster, 
				verb=_('replied to your comment on the question'),
				target=question,
				category=Notification.ACTIVITY
			)
			
		for follower in question.followers.all():
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

		with transaction.atomic():
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

	def downvote_comment(self, comment, output=False, for_html=False):
		poster = comment.poster

		# user can't downvote(vote for his own answer(post))
		if self == poster:
			return (
				False,
				_("You can't add a dislike to your own comment.")
			)

		# staff can always downvote comment
		if not self.is_staff:
			# user doesn't have enough points to downvote
			if self.site_points < REQUIRED_DOWNVOTE_POINTS:
				if for_html:
					return (
						False, 
						_("You need at least <strong>{} points</strong> to be able to add a dislike to this comment.").format(REQUIRED_DOWNVOTE_POINTS)
					)

				return (
					False, 
					_("You need at least {} points to be able to add a dislike to this comment.").format(REQUIRED_DOWNVOTE_POINTS)
				)

		# Handle points only if comment is parent(answer)
		if comment.is_parent:
			with transaction.atomic():
				# see core/constants.py file; comment under `RESTRICTED_POINTS` for explanation.
				owner_points = poster.site_points
				if owner_points == RESTRICTED_POINTS:
					owner_points = RESTRICTED_POINTS + 1
					# first update database so as to leverage F expressions
					poster.save(update_fields=['site_points'])

				# penalise question owner for downvote
				new_points = F('site_points') + ANSWER_DOWNVOTE_POINTS_CHANGE
				if new_points < THRESHOLD_POINTS:
					new_points = THRESHOLD_POINTS

				poster.site_points = new_points
				poster.save(update_fields=['site_points'])
				comment.downvoters.add(self)
		else:
			comment.downvoters.add(self)

		return (True, comment.downvote_count) if output else (True, '')

	# Verify if user can edit or delete posts ##
	# NOTE that if any argument is added to any of these functions,
	# some functionalities will break, including the template filters in core/template_tags module.
	def can_edit_question(self, question):
		"""
		Verify if user is permitted to edit question
		
		To test if a user can edit a question.
		- Questions with (3 score or 3 answers) and above can't be edited
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

	def can_edit_comment(self, comment):
		"""
		To test if a user can edit an comment.
		- Only poster can edit comment
		- Comments with 4+ score can't be edited
		"""
		
		if comment.score > COMMENT_CAN_EDIT_VOTE_LIMIT:
			return False

		if self.id == comment.poster_id:
			return True

		return False

	def can_delete_comment(self, comment):
		"""
		To test if a user can delete a comment.
		- Staff can delete any comment
		- Moderator can delete only flagged comments
		- Comments with 4 upvotes and above can't be deleted by mod nor poster.
		- Poster can delete comment
		"""
					
		if self.is_staff:
			return True

		# if it is flagged, moderator can delete.
		if self.is_mod and Flag.objects.is_flagged(comment):
			return True

		# verify if comment can be deleted
		if comment.score > COMMENT_CAN_DELETE_VOTE_LIMIT:
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
		- After 30mins, comment can't be edited
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
		- poster can delete comment; other users nope.
		"""
					
		if self.is_staff:
			return True

		# if it is flagged, moderator can delete.
		if self.is_mod and Flag.objects.is_flagged(comment):
			return True
			
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

