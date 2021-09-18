from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.signals import (
    pre_save, post_save,
    pre_delete, post_delete, m2m_changed
)
from django.utils.translation import gettext_lazy as _
from notifications.signals import notify

from core.constants import MAX_TAGS_PER_QUESTION
from .models import (
    AcademicQuestion, AcademicQuestionComment,
    AcademicAnswer, SchoolAnswer, SchoolQuestion,
	AcademicAnswerComment, SchoolQuestionComment,
	SchoolAnswerComment
)

User = get_user_model()

# Notifications will be send(to owner) when
	# post is liked or disliked 
	# a comment is added to his post
	# answer is added to his question
	# 

def post_upvoted(sender, instance, action, **kwargs):
	"""Triggerred when a post(question or answer) is liked."""

	# Notify owner of post
	print(instance)
	# before upvote has been added, verify if user is in upvotes 
	if action == 'pre_add':
		pass


def post_downvoted(sender, **kwargs):
	return


# Signal.connect(receiver, sender=None, weak=True, dispatch_uid=None)
# m2m_changed.connect(post_upvoted, sender=AcademicQuestion.upvoters.through)
# m2m_changed.connect(post_downvoted, sender=AcademicQuestion.downvoters.through)
# m2m_changed.connect(post_upvoted, sender=AcademicAnswer.upvoters.through)
# m2m_changed.connect(post_downvoted, sender=AcademicAnswer.downvoters.through)
# post_save.connect(answer_added, sender=AcademicAnswer)
# post_save.connect(question_comment_added, sender=AcademicQuestionComment)
# post_save.connect(answer_comment_added, sender=AcademicAnswerComment)

# m2m_changed.connect(post_upvoted, sender=SchoolQuestion.upvoters.through)
# m2m_changed.connect(post_downvoted, sender=SchoolQuestion.downvoters.through)
# m2m_changed.connect(post_upvoted, sender=SchoolAnswer.upvoters.through)
# m2m_changed.connect(post_downvoted, sender=SchoolAnswer.downvoters.through)
# post_save.connect(answer_added, sender=SchoolAnswer)
# post_save.connect(question_comment_added, sender=SchoolQuestionComment)
# post_save.connect(answer_comment_added, sender=SchoolAnswerComment)


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