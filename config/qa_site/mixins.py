from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext_lazy as _

from core.constants import (
	MAX_ANSWERS_PER_USER_PER_QUESTION, QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT,
	QUESTION_CAN_EDIT_VOTE_LIMIT, ANSWER_CAN_EDIT_VOTE_LIMIT,
	COMMENT_CAN_EDIT_TIME_LIMIT, COMMENT_CAN_EDIT_UPVOTE_LIMIT,
	QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT, QUESTION_CAN_DELETE_VOTE_LIMIT, 
	ANSWER_CAN_DELETE_VOTE_LIMIT, COMMENT_CAN_DELETE_UPVOTE_LIMIT
)
from flagging.models import Flag


class CanEditQuestionMixin(LoginRequiredMixin, UserPassesTestMixin):
	"""
	To test if a user can edit a question.
	- Questions with (3 vote_count or 2 answers) and above can't be edited
	- Only poster can edit question
	"""

	def test_func(self):
		user, self.object = self.request.user, self.get_object()
		question = self.object
		
		# first verify if question can be edited
		if question.vote_count > QUESTION_CAN_EDIT_VOTE_LIMIT or question.num_answers > QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT:
			return False

		# now verify if user is poster
		if user == question.poster:
			return True
		
	def get_permission_denied_message(self):
		# self.object will be set by the `test_func`
		user, question = self.request.user, self.object

		if user != question.poster:
			return _("You can only edit your own questions.")

		if question.vote_count > QUESTION_CAN_EDIT_VOTE_LIMIT or question.num_answers > QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT:
			return _(
				"You can only edit questions with less than {} votes(number of likes - number of dislikes) or less than {} answers. You may post a new question.".format(QUESTION_CAN_EDIT_VOTE_LIMIT, QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT)
			)
		return super().get_permission_denied_message()


class CanEditAnswerMixin(LoginRequiredMixin, UserPassesTestMixin):
	"""
	To test if a user can edit an answer.
	- Answers with (5 vote_count) and above can't be edited
	- Only poster can edit answer
	"""

	def test_func(self):
		user, self.object = self.request.user, self.get_object()
		answer = self.object
		
		# first verify if answer can be edited
		if answer.vote_count > ANSWER_CAN_EDIT_VOTE_LIMIT:
			return False

		# now verify if user is poster
		if user == answer.poster:
			return True
		
	def get_permission_denied_message(self):
		# self.object will be set by the `test_func`
		user, answer = self.request.user, self.object

		if user != answer.poster:
			return _("You can only edit your own answers.")

		if answer.vote_count > ANSWER_CAN_EDIT_VOTE_LIMIT:
			return _(
				"You can only edit answers with less than {} votes(number of likes - number of dislikes). You may post a new answer if you have less than {} answers to this question.".format(ANSWER_CAN_EDIT_VOTE_LIMIT, MAX_ANSWERS_PER_USER_PER_QUESTION)
			)
		return super().get_permission_denied_message()


class CanEditCommentMixin(LoginRequiredMixin, UserPassesTestMixin):
	"""
	To test if a user can edit an comment.
	- Only poster can edit comment
	- After 5 minutes, comments can't be edited.
	- Comments with 5 upvotes and above can't be edited
	"""

	def test_func(self):
		user, self.object = self.request.user, self.get_object()
		comment = self.object
		
		# first verify if comment can be edited
		if (comment.upvote_count > COMMENT_CAN_EDIT_UPVOTE_LIMIT) or not comment.is_within_edit_timeframe:
			return False

		# now verify if user is poster
		if user == comment.poster:
			return True
		
	def get_permission_denied_message(self):
		# self.object will be set by the `test_func`
		user, comment = self.request.user, self.object

		if user != comment.poster:
			return _("You can only edit your own comments.")

		if comment.upvote_count > COMMENT_CAN_EDIT_UPVOTE_LIMIT:
			return _(
				"You can only edit comments with less than {} likes. You may post a new comment.".format(COMMENT_CAN_EDIT_UPVOTE_LIMIT)
			)
		
		# if comment is not in edit timeframe
		if not comment.is_within_edit_timeframe:
			return _(
				"You can only edit comments that are less than {} minutes old.".format(COMMENT_CAN_EDIT_TIME_LIMIT)
			)

		return super().get_permission_denied_message()


class CanDeleteQuestionMixin(LoginRequiredMixin, UserPassesTestMixin):
	"""
	To test if a user can delete a question.
	- Staff can delete any question(any post)
	- Moderator can delete only flagged questions(posts)
	- Poster can delete question only if it has less than 3 votes or less than 2 answers
	"""

	def test_func(self):
		user, self.object = self.request.user, self.get_object()
		question = self.object

		if user.is_staff:
			return True

		# if listing is flagged moderator can delete it.
		# first verify if question is flagged before verifying number of answers...
		# coz there could be cases where a question has say 2 "bizarre" answers.. and it could be flagged
		# so if it is flagged, moderator can delete.
		if user.is_mod and Flag.objects.is_flagged(question):
			return True
		
		# verify if question can be deleted
		if question.vote_count > QUESTION_CAN_DELETE_VOTE_LIMIT or question.num_answers > QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT:
			return False

		# now verify if user is owner
		if user == question.poster:
			return True
		
	def get_permission_denied_message(self):
		# self.object will be set by the `test_func`
		user, question = self.request.user, self.object

		if user.is_mod:
			return _("Moderators can only delete flagged questions")

		if user != question.poster:
			return _("You can only delete your own questions.")

		if question.vote_count > QUESTION_CAN_DELETE_VOTE_LIMIT or question.num_answers > QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT:
			return _(
				"You can only delete questions with less than {} votes(number of likes - number of dislikes) or less than {} answers. This question may help future users.".format(QUESTION_CAN_DELETE_VOTE_LIMIT, QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT)
			)
		return super().get_permission_denied_message()


class CanDeleteAnswerMixin(LoginRequiredMixin, UserPassesTestMixin):
	"""
	To test if a user can delete an answer.
	- Staff can delete any answer
	- Moderator can delete only flagged answers
	- Poster can delete answer only if it has less than 3 votes
	"""

	def test_func(self):
		user, self.object = self.request.user, self.get_object()
		answer = self.object

		if user.is_staff:
			return True
		
		# if it is flagged, moderator can delete.
		if user.is_mod and Flag.objects.is_flagged(answer):
			return True

		# verify if answer can be deleteed
		if answer.vote_count > ANSWER_CAN_DELETE_VOTE_LIMIT:
			return False

		# now verify if user is poster
		if user == answer.poster:
			return True
		
	def get_permission_denied_message(self):
		# self.object will be set by the `test_func`
		user, answer = self.request.user, self.object

		if user.is_mod:
			return _("Moderators can only delete flagged answers")

		if user != answer.poster:
			return _("You can only delete your own answers.")

		if answer.vote_count > ANSWER_CAN_DELETE_VOTE_LIMIT:
			return _(
				"You can only delete answers with less than {} votes(number of likes - number of dislikes). This answer may help future users.".format(ANSWER_CAN_DELETE_VOTE_LIMIT)
			)
		return super().get_permission_denied_message()


class CanDeleteCommentMixin(LoginRequiredMixin, UserPassesTestMixin):
	"""
	To test if a user can delete a comment.
	- Staff can delete any comment
	- Moderator can delete only flagged comments
	- Comments with 5 upvotes and above can't be deleted
	- Poster can delete comment
	"""

	def test_func(self):
		user, self.object = self.request.user, self.get_object()
		comment = self.object

		if user.is_staf:
			return True

		# if it is flagged, moderator can delete.
		if user.is_mod and Flag.objects.is_flagged(comment):
			return True

		# verify if comment can be deleted
		if comment.upvote_count > COMMENT_CAN_DELETE_UPVOTE_LIMIT:
			return False

		# now verify if user is poster
		if user == comment.poster:
			return True
		
	def get_permission_denied_message(self):
		# self.object will be set by the `test_func`
		user, comment = self.request.user, self.object

		if user.is_mod:
			return _("Moderators can delete only flagged comments.")

		if user != comment.poster:
			return _("You can only delete your own comments.")

		if comment.upvote_count > COMMENT_CAN_DELETE_UPVOTE_LIMIT:
			return _(
				"You can only delete comments with less than {} likes. This comment may help future users.".format(COMMENT_CAN_DELETE_UPVOTE_LIMIT)
			)
		return super().get_permission_denied_message()

