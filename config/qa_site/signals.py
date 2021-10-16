from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from notifications.signals import notify

from core.constants import MAX_TAGS_PER_QUESTION
from .models import (
	SchoolQuestion, AcademicQuestionComment, AcademicAnswerComment, 
	SchoolQuestionComment, SchoolAnswerComment
)

User = get_user_model()


# @receiver(post_save, sender=AcademicQuestionComment)
def comment_posted(sender, instance, created, **kwargs):
	"""Send notifications to users mentioned in this comment"""
	# print('comment_posted signal called')
	# if comment is new
	if created:    
		# TODO get mentioned users and send notifications to them
		pass

	# if comment was updated
	else:
		# update mentioned users. (comment.users_mentioned.set(list of newly mentioned users))
		# notify newly mentioned users
		# there's no much problem in modifying newly mentioned users
		# since after 5 minutes, comment can't be edited.
		pass
	

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
# m2m_changed.connect(tags_changed, sender=SchoolQuestion.tags.through)


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
# m2m_changed.connect(tags_changed, sender=SchoolQuestion.tags.through)

