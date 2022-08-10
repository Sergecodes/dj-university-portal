from django.contrib.auth import get_user_model
# from django.core.exceptions import ValidationError
# from django.db.models.signals import m2m_changed, pre_save, post_save
# from django.dispatch import receiver
# from django.utils.translation import gettext_lazy as _
# from notifications.signals import notify

# from core.constants import MAX_TAGS_PER_QUESTION
# from .models import (
# 	DiscussQuestion, AcademicQuestionComment, 
# 	AcademicAnswerComment, DiscussComment,
# )
from .utils import extract_mentions

User = get_user_model()


def set_users_mentioned(sender, instance, created, **kwargs):
	# Note that update_fields will always be in kwargs since it is a part of the 
	# function parameters, but it will be None(it won't be an empty list )
	# if it does not contain any fields.
	# So if the field is None, set it to an empty list
	update_fields = kwargs.get('update_fields')
	if not update_fields:
		update_fields = []

	comment = instance

	if created or 'content' in update_fields:
		mentioned_users = []

		for username in extract_mentions(comment.content):
			try:
				mentioned_users.append(User.objects.get(username=username))
			except User.DoesNotExist:
				pass

		comment.users_mentioned.set(mentioned_users, clear=True)


# def tags_changed(sender, instance, action, **kwargs):
# 	"""Limit number of tags per school question"""
# 	pk_set = kwargs.get('pk_set')
# 	num_new_tags = len(pk_set)

# 	if action == "pre_add":
# 		if (num_tags := instance.tags.count()) + num_new_tags > MAX_TAGS_PER_QUESTION:
# 			raise ValidationError(
# 				_(f"Each question should have maximum {MAX_TAGS_PER_QUESTION} tags but this one would have had {num_tags + MAX_TAGS_PER_QUESTION} tags.")
# 			)

# # m2m_changed.connect(tags_changed, sender=AcademicQuestion.tags.through)
# m2m_changed.connect(tags_changed, sender=DiscussQuestion.tags.through)


# def tags_changed(sender, instance, action, **kwargs):
# 	"""Limit number of tags per school question"""
# 	pk_set = kwargs.get('pk_set')
# 	num_new_tags = len(pk_set)

# 	if action == "pre_add":
# 		if (num_tags := instance.tags.count()) + num_new_tags > MAX_TAGS_PER_QUESTION:
# 			raise ValidationError(
# 				_(f"Each question should have maximum {MAX_TAGS_PER_QUESTION} tags but this one would have had {num_tags + MAX_TAGS_PER_QUESTION} tags.")
# 			)

# # m2m_changed.connect(tags_changed, sender=AcademicQuestion.tags.through)
# m2m_changed.connect(tags_changed, sender=DiscussQuestion.tags.through)

