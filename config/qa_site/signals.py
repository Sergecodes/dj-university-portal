from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.utils.translation import gettext_lazy as _

from core.constants import MAX_TAGS_PER_QUESTION
from .models import SchoolQuestion


def tags_changed(sender, instance, action, **kwargs):
	"""Limit number of tags per school question"""
	pk_set = kwargs.get('pk_set')
	num_new_tags = len(pk_set)

	if action == "pre_add":
		if (num_tags := instance.tags.count()) + num_new_tags > MAX_TAGS_PER_QUESTION:
			raise ValidationError(
				_(f"Each question should have maximum {MAX_TAGS_PER_QUESTION} tags but this one would have had {num_tags + MAX_TAGS_PER_QUESTION} tags.")
			)

# m2m_changed.connect(tags_changed, sender=AcademicQuestion.tags.through)
m2m_changed.connect(tags_changed, sender=SchoolQuestion.tags.through)



# from django.db.models.signals import post_save
# from notifications.signals import notify
# from qa_site.models import MyModel

# def my_handler(sender, instance, created, **kwargs):
# 	notify.send(instance, verb='was saved')

# post_save.connect(my_handler, sender=MyModel)

# notify.send(actor, recipient, verb, action_object, target, level, description, public, timestamp, **kwargs)