from django.conf import settings
from django.db import models
from django.db.models.fields.files import FieldFile, ImageFieldFile
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from core.utils import parse_email

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
	

class ModifyingFieldDescriptor:
	"""Modifies a field when set using the field's overriden .to_python() method"""
	def __init__(self, field):
		self.field = field

	def __get__(self, instance, owner=None):
		if instance is None:
			raise AttributeError('Can only be accessed via an instance.')
		return instance.__dict__[self.field.name]

	def __set__(self, instance, value):
		instance.__dict__[self.field.name] = self.field.to_python(value)


class NormalizedEmailField(models.EmailField):
	""" Override EmailField to convert emails to lowercase before saving """
	description = "Convert email to lowercase and convert 'googlemail' to 'gmail'"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def to_python(self, value):
		if not value:
			return ''
		return parse_email(value)

	def contribute_to_class(self, cls, name, private_only=False):
		super().contribute_to_class(cls, name)
		setattr(cls, self.name, ModifyingFieldDescriptor(self))



