from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.constants import PROFILE_IMAGE_UPLOAD_DIR
from marketplace.models import Institution
from past_papers.models import PastPaper


class SocialMediaFollow(models.Model):
	"""Links to user's social media profiles"""
	twitter_follow = models.CharField(
		_('Twitter link or username'),
		max_length=50,
		blank=True, null=True
	)
	facebook_follow = models.CharField(
		_('Facebook link or username'),
		max_length=50,
		blank=True, null=True
	)
	instagram_follow = models.CharField(
		_('Instagram link or username'),
		max_length=50,
		blank=True, null=True
	)
	tiktok_follow = models.CharField(
		_('Tiktok link or username'),
		max_length=50,
		blank=True, null=True
	)
	github_follow = models.CharField(
		_('Github link or username'),
		max_length=50,
		blank=True, null=True
	)
	website_follow = models.CharField(
		_('Other website links'),
		help_text=_('An example could be a link to a YouTube channel or Likee profile, etc.. <br> Separate multiple links with a semicolon.'),
		max_length=250,
		blank=True, null=True
	)


class SocialProfile(models.Model):
	GENDERS = (
		('M', _('Male')), 
		('F', _('Female'))   
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

	LEVELS = (
		('N/A', '--------'),  # this comma is required to create a tuple !
	) + PastPaper.LEVELS

	level = models.CharField(_('Level'), choices=LEVELS, max_length=5, default='N/A')
	about_me = models.TextField(_('A little about me'))
	hobbies = models.TextField(_('My hobbies and interests'))
	profile_image = models.ImageField(
		upload_to=PROFILE_IMAGE_UPLOAD_DIR, 
		null=True, blank=True
	)
	birth_date = models.DateField(
		_('Birthday'), 
		help_text=_("Please at least enter the correct birth year.")
	)
	department = models.CharField(
		_('Department'),
		max_length=30
	)
	user = models.OneToOneField(
		get_user_model(),
		on_delete=models.CASCADE,
		related_name='social_profile',
		# related_query_name='social_profile'  # related_query_name = related_name if rel_name is specified
		primary_key=True
	)
	social_media = models.OneToOneField(
		SocialMediaFollow, 
		related_name='+',
		on_delete=models.SET_NULL,
		null=True, blank=True  
	)
	school = models.ForeignKey(
		Institution,
		on_delete=models.PROTECT,
		related_name='social_profiles',
		related_query_name='social_profile'
	)
	current_relationship = models.CharField(
		_('Current relationship'),
		choices=CURRENT_RELATIONSHIPS, 
		max_length=15,
		default=None
	)
	interested_relationship = models.CharField(
		_('Interested relationship'),
		choices=INTERESTED_RELATIONSHIPS, 
		max_length=15,
		default=None
	)
	gender = models.CharField(
		_('Gender'),
		choices=GENDERS, 
		default='M', 
		max_length=2
	)
	creation_datetime = models.DateTimeField(auto_now_add=True)
	# determine if users profile page is visible to other users
	# is_visible = models.BooleanField(
	# 	_('Profile visible to other users'),
	# 	default=False, 
	# 	help_text=_("<br>Enable <em>Socialize</em> and allow other users to be able to view my social profile.")
	# )

	class Meta:
		ordering = ['-creation_datetime']
		indexes = [
			models.Index(fields=['-creation_datetime'])
		]

	@property
	def profile_filename(self):
		"""
		Get file name of file with extension (not relative path from MEDIA_URL).
		If files have the same name, Django automatically appends a unique string to each file before storing.
		This property(function) returns the name of a file (on disk) without its extension.
		Ex. `Screenshot_from_2020_hGETyTo`  or `Screenshot_from_2020`. 
		Equivalent to the `title` field in some File models.
		"""
		if (image := self.profile_image):
			import os

			name_with_extension = os.path.basename(image.name)
			return name_with_extension.split('.')[0]
		return ''

	@property
	def age(self):
		"""Get user's age from birth_date"""
		time_delta = timezone.now().date() - self.birth_date
		return int(time_delta.days / 365)
		
	@property
	def actual_gender(self):
		"""Get full representation of user's gender"""
		return _('Male') if self.gender == 'M' else _('Female')

	@property
	def age_range(self):
		# AGE_CHOICES = (
		# 	(0, _('Any Age')),
		# 	(1, _('15 Below')),
		# 	(2, _('16 - 19')),
		# 	(3, _('20 - 25')), 
		# 	(4, _('26 - 29')),
		# 	(5, _('30 Above')),
		# )

		age = self.age

		if age <= 15:
			return _('15 Below')
		elif age >= 16 and age <= 19:
			return _('16 - 19')
		elif age >= 20 and age <= 25:
			return _('20 - 25')
		elif age >= 26 and age <= 29:
			return _('26 - 29')
		else:
			return _('30 Above')

	def get_absolute_url(self):
		return reverse('socialize:view-profile', kwargs={'username': self.user.username})

	def __str__(self):
		return str(self.user)



