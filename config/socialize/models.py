from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.constants import PROFILE_IMAGE_UPLOAD_DIR, GENDERS
from core.models import Institution
from past_papers.models import PastPaper

User = get_user_model()


class SocialProfileManager(models.Manager):
	def get_site_profile(self):
		"""Get CamerSchools social profile"""
		user_account = User.objects.get_site_account()

		try:
			social_profile = SocialProfile.objects.get(user=user_account)
		except SocialProfile.DoesNotExist:
			# if social profile isn't present, create it
			social_media = SocialMediaFollow.objects.create(
				twitter_follow='https:twitter.com/...',
				website_follow='https://www.camerschools.com',
			)

			social_profile = SocialProfile.objects.create(
				user=user_account,
				social_media=social_media,
				about_me='Nothing about me for now...',
				hobbies='No hobbies for now',
				birth_date=timezone.now(),
				department='Computer Science',
				original_language='en',
			)

		return social_profile


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
	CURRENT_RELATIONSHIPS = (
		('single', _('Single')),
		('dating', _('Dating')),
		('engaged', _('Engaged')),
		('married', _('Married')),
		('undecided', _('Undecided'))
	)

	# use list instead of tuple to enable modification in social profile filter.
	# see socialize/views/SocialProfileFilter...
	# any modifications done to this list should be ammended in the filter.
	INTERESTED_RELATIONSHIPS = [
		('none', _('Not interested')),
		('chatting', _('Being chat pals')), 
		('studies', _('Being study pals')),
		('clubbing', _('Clubbing this weekend')),
		('dating', _('Dating')),
		('flirting', _('Flirting')),
		('friendship', _('Friendship')),
		('hanging_out', _('Hanging out this weekend')),
		('marriage', _('Marriage')),
		('undecided', _('Undecided'))
	]

	LEVELS = (
		('N/A', '--------'),  # this comma is required to create a tuple !
	) + PastPaper.LEVELS

	level = models.CharField(_('Level'), choices=LEVELS, max_length=5, default='N/A')
	about_me = models.TextField(_('A little about me'), blank=True)
	hobbies = models.TextField(_('My hobbies and interests'), blank=True)
	profile_image = models.ImageField(
		upload_to=PROFILE_IMAGE_UPLOAD_DIR, 
		null=True, blank=True
	)
	birth_date = models.DateField(
		_('Birthday'), 
		help_text=_( 
			"Please at least enter the correct birth year. <br>" 
			"Your birth date and age won't be visible to other users."
		)
	)
	department = models.CharField(
		_('Department'),
		max_length=30,
		help_text=_("Enter your study speciality")
	)
	user = models.OneToOneField(
		User,
		on_delete=models.CASCADE,
		# related_query_name='social_profile'  
		# related_query_name = related_name if related_name is specified
		related_name='social_profile',
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
		on_delete=models.SET_NULL,
		null=True, blank=True,
		related_name='social_profiles',
		related_query_name='social_profile'
	)
	current_relationship = models.CharField(
		_('Current relationship'),
		choices=CURRENT_RELATIONSHIPS, 
		max_length=15,
		default='single'
	)
	interested_relationship = models.CharField(
		_('Interested relationship'),
		choices=INTERESTED_RELATIONSHIPS, 
		max_length=15,
		default='none'
	)
	gender = models.CharField(
		_('Gender'),
		choices=GENDERS, 
		default='M', 
		max_length=2
	)
	creation_datetime = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)
	original_language = models.CharField(choices=settings.LANGUAGES, max_length=2, editable=False)
	view_count = models.PositiveIntegerField(default=0)
	# determine if users profile page is visible to other users
	# is_visible = models.BooleanField(
	# 	_('Profile visible to other users'),
	# 	default=False, 
	# 	help_text=_("<br>Enable <em>Socialize</em> and allow other users to be able to view my social profile.")
	# )

	objects = SocialProfileManager()

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



