from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants import PROFILE_IMAGE_UPLOAD_DIR
from marketplace.models import Institution


class SocialMediaFollow(models.Model):
	"""Links to user's social media profiles"""
	twitter_follow = models.CharField(
		_('Twitter link or username'),
		max_length=30,
		blank=True, null=True
	)
	facebook_follow = models.CharField(
		_('Facebook link or username'),
		max_length=30,
		blank=True, null=True
	)
	instagram_follow = models.CharField(
		_('Instagram link or username'),
		max_length=30,
		blank=True, null=True
	)


class SocialProfile(models.Model):
	GENDERS = (
		('M', _('Male')), 
		('F', _('Female'))   
	)

	LEVELS = (
		('L1', _('Level 1')),
		('L2', _('Level 2')),
		('L3', _('Level 3')),
		('L4', _('Level 5')),
		('M', _('Masters')),
		('PhD', _('Doctorate')),
		(_('Other'), _('Other')),
	)

	CURRENT_RELATIONSHIPS = (
		('single', _('Single')),
		('dating', _('Dating')),
		('engaged', _('Engaged')),
		('married', _('Married')),
		('undecided', _('Undecided'))
	)

	INTERESTED_RELATIONSHIPS = (
		('chatting', _('Being chat pals')), 
		('studies', _('Being study pals')),
		('clubbing', _('Clubbing this weekend')),
		('dating', _('Dating')),
		('flirting', _('Flirting')),
		('friendship', _('Friendship')),
		('hanging_out', _('Hanging out this weekend')),
		('marriage', _('Marriage')),
		('undecided', _('Undecided'))
	)

	user = models.OneToOneField(
		get_user_model(),
		on_delete=models.CASCADE,
		related_name='social_profile',
		# related_query_name='social_profile'  # related_query_name = related_name if rel_name is specified
		primary_key=True
	)
	level = models.CharField(choices=LEVELS, max_length=7)
	social_media = models.OneToOneField(
		SocialMediaFollow, 
		on_delete=models.SET_NULL,
		related_name='+',
		null=True, blank=True
	)
	school = models.ForeignKey(
		Institution,
		on_delete=models.PROTECT,
		related_name='social_profiles',
		related_query_name='social_profile'
	)
	current_relationship = models.CharField(
		choices=CURRENT_RELATIONSHIPS, 
		max_length=15
	)
	interested_relationship = models.CharField(
		choices=INTERESTED_RELATIONSHIPS, 
		max_length=15
	)
	gender = models.CharField(
		choices=GENDERS, 
		default='M', 
		max_length=2
	)
	about_me = models.TextField(_('A little about me'))
	interests = models.TextField(_('My interests'))
	hobbies = models.TextField(_('My hobbies'))
	profile_image = models.ImageField(
		upload_to=PROFILE_IMAGE_UPLOAD_DIR, 
		null=True, blank=True
	)
	# determine if users profile page is visible to other users
	is_visible = models.BooleanField(
		default=False, 
		help_text=_("Enable Socialize and allow other users to be able to view my profile.")
	)
	birth_date = models.DateField(
		_('Birthday'), 
		help_text=_("Please at least enter the correct birth year.")
	)



