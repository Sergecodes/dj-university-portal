from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils import parse_email


class ModifyingFieldDescriptor:
	""" Modifies a field when set using the field's overriden .to_python() method """
	def __init__(self, field):
		self.field = field

	def __get__(self, instance, owner=None):
		if instance is None:
			raise AttributeError('Can only be accessed via an instance.')
		return instance.__dict__[self.field.name]

	def __set__(self, instance, value):
		instance.__dict__[self.field.name] = self.field.to_python(value)


class FullNameField(models.CharField):
	""" Convert string to title case. eg 'I am GOOD-yy => I Am Good-Yy """
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def to_python(self, value):
		return value.title()

	def contribute_to_class(self, cls, name, private_only=False):
		super().contribute_to_class(cls, name)
		setattr(cls, self.name, ModifyingFieldDescriptor(self))


class NormalizedEmailField(models.EmailField):
	""" Override EmailField to convert emails to lowercase before saving """
	description = _("Convert email to lowercase and convert 'googlemail' to 'gmail'.")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def to_python(self, value):
		return parse_email(value)

	def contribute_to_class(self, cls, name, private_only=False):
		super().contribute_to_class(cls, name)
		setattr(cls, self.name, ModifyingFieldDescriptor(self))

