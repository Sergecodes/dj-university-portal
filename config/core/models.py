from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.model_fields import NormalizedEmailField, FullNameField
from flagging.models import Flag


class Institution(models.Model):
	# only staff can add school.
	name = models.CharField(_('Name'), max_length=50, unique=True)
	location = models.CharField(
		_('Location'),
		max_length=60,
		help_text=_('Street or quarter where institution is located')
	)
	datetime_added = models.DateTimeField(_('Date/time added'), auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name


class Post(models.Model):
	"""Abstract model to describe an item post."""

	flags = GenericRelation(Flag)
	view_count = models.PositiveIntegerField(default=0)
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
	contact_name = FullNameField(
		_('Full name'),
		max_length=25,
		help_text=_('Please use your real names.'),
		# validators=[validate_full_name]
	)
	contact_numbers = models.ManyToManyField(
		'users.PhoneNumber',
		related_name='+'
	)
	contact_email = NormalizedEmailField(
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

