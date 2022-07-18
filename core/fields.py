# Ref: https://docs.djangoproject.com/en/3.2/ref/models/fields/#field-api-reference

from django.conf import settings
from django.db import models
from django.db.models.fields.files import FieldFile, ImageFieldFile
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

STORAGE = import_string(settings.DEFAULT_FILE_STORAGE)()


class DynamicStorageFieldFile(FieldFile):
	def __init__(self, instance, field, name):
		super().__init__(instance, field, name)
		self.storage = STORAGE


class DynamicStorageImageFieldFile(ImageFieldFile):
	def __init__(self, instance, field, name):
		super().__init__(instance, field, name)
		self.storage = STORAGE


class DynamicStorageFileField(models.FileField):
	"""
	Enable dynamically changing storage backend, 
	such as switching between AWS S3 and local storage
	"""
	attr_class = DynamicStorageFieldFile

	def pre_save(self, model_instance, add):
		self.storage = STORAGE
		model_instance.file.storage = STORAGE

		file = super().pre_save(model_instance, add)
		return file


class DynamicStorageImageField(models.ImageField):
	"""
	Enable dynamically changing storage backend, 
	such as switching between AWS S3 and local storage
	"""
	attr_class = DynamicStorageImageFieldFile

	def pre_save(self, model_instance, add):
		self.storage = STORAGE
		model_instance.file.storage = STORAGE

		file = super().pre_save(model_instance, add)
		return file
	

class NormalizedEmailField(models.EmailField):
    description = "An email field that replaces @googlemail.com to @gmail.com since both are actually the same"
   
    def _parse_value(self, value: str):
      # Remember username@googlemail.com and username@gmail.com point to the same gmail account.
      # see mailigen.com/blog/does-capitalization-matter-in-email-addresses/
      from django.contrib.auth.models import UserManager

      value = UserManager.normalize_email(value)
      return value.replace('@googlemail.com', '@gmail.com')

    def get_prep_value(self, value):
        # When storing to db
        value = super().get_prep_value(value)
        if value is None:
            return None
        return self._parse_value(str(value))

    def to_python(self, value):
        # When displaying
        if value is None:
            return value
        return self._parse_value(str(value))

    def from_db_value(self, value, expression, connection):
        # After retrieving from db
        return self.to_python(value)

