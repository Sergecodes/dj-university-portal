from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet, Manager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserQuerySet(QuerySet):
	def delete(self):
		# self is a queryset containing the profiles to be deleted; Profile.objects.filter(...).delete()
		# get users from self
		# note: we can't do something like this: Entry.objects.update(blog__name='foo') # Won't work!
		# update() only works on the model's fields, not it's related fields.
		get_user_model().objects.filter(id__in=self).update(is_active=False)
		self.update(status='D', deletion_datetime=timezone.now())


class UserManager(BaseUserManager, Manager):
	def create_user(self, email, username, full_name, password, gender, first_language, commit=True, **extra_fields):
		""" Create and save a user with the given email, username, password, etc... . Call this method with appropriate fields because no validation will be performed here, data will be instantly saved to the database. """
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
		
		email = self.normalize_email(email)
		# validate_email(email)

		# validate_username = UnicodeUsernameValidator()
		# validate_username(username)

		# validate_full_name(full_name)
		
		user = self.model(
			email=email, 
			username=username, 
			full_name=full_name, 
			gender=gender,
			first_language=first_language,
			**extra_fields
		)
		user.set_password(password)

		if commit:
			user.save(using=self._db)

		return user

	def create_superuser(self, email, username, full_name, password, gender, first_language, **extra_fields):
		""" Create and save a SuperUser with the given email, name, full name, password etc... """
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

	def active(self):
		return self.model.objects.filter(status='A')

	def deleted(self):
		return self.model.objects.filter(status='D')

	def suspended(self):
		return self.model.objects.filter(status='S')

