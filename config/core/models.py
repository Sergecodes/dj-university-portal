from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import gettext_lazy as _
from notifications.base.models import AbstractNotification

from core.model_fields import LowerCaseEmailField, TitleCaseField
from flagging.models import Flag


class Post(models.Model):
	"""Abstract model to describe an item post."""

	flags = GenericRelation(Flag)
	# tags will be obtained from the name of the item. ex. red pen => 'red', 'pen'
	# tags = TaggableManager()
	# i don't see the need for tags. todo search via normal field with search vector(Postgres) form more efficiency
	slug = models.SlugField(max_length=255)
	posted_datetime = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)
	# when the post will be considered expired. see save method for implementation
	# expiry_datetime = models.DateTimeField()
	original_language = models.CharField(
		choices=settings.LANGUAGES,
		max_length=2,
		help_text=_('Language in which post was created'),
		editable=False
	)
	contact_name = TitleCaseField(
		_('Full name'),
		max_length=25,
		help_text=_('Please use your real names.'),
		# validators=[validate_full_name]
	)
	contact_numbers = models.ManyToManyField(
		'users.PhoneNumber',
		related_name='+'
	)
	contact_email = LowerCaseEmailField(
		_('Email address'),
		max_length=50,
		help_text=_("Email address to contact; enter a valid email."),
		validators=[validate_email]
	)

	# def save(self, *args, **kwargs):
	# 	if not self.id:
	# 		self.expiry_datetime = self.posted_datetime + VALIDITY_PERIOD
	# 	super().save(*args, **kwargs)

	# @property
	# def is_outdated(self):
	# 	"""Returns whether a post is outdated(has expired)"""
	# 	return self.expiry_datetime < timezone.now()

	class Meta:
		abstract = True


## Override the django-notifications-hq Notification model
class Notification(AbstractNotification):
    GENERAL = 'G'       # general notifications
    MENTION = 'M'       # to users that were mentioned in comments(qa_site only)
    ACTIVITY = 'A'      # to post owners, when their post has an activity
    FLAG = 'F'          # to users whose post has been flagged
    REPORTED = 'R'      # moderators only, for reported posts
    FOLLOWING = 'FF'    # for users that are following a post

    CATEGORIES = (
        (GENERAL, _('General')),
        (MENTION, _('Mention')),
        (ACTIVITY, _('Activity')),
        (FLAG, _('Flag')),
        (FOLLOWING, _('Following')),
        (REPORTED, _('Reported'))
    )

    category = models.CharField(choices=CATEGORIES, default='G', max_length=2)
    # url to go to; useful for general notifications
    follow_url = models.URLField(blank=True, null=True)
    # used in REPORTED notifications to check whether a post(flag) has been absolved or not
    # as said in the docs, "the default value of BooleanField is None when Field.default isn't defined."
    # we set null=True so it is nullable, to account for notifcations that don't use this field.
    absolved = models.BooleanField(null=True)


    class Meta(AbstractNotification.Meta):
        abstract = False
        app_label = 'core'




