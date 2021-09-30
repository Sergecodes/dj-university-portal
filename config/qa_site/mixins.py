from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext_lazy as _

from core.constants import (
	MAX_ANSWERS_PER_USER_PER_QUESTION, QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT,
	QUESTION_CAN_EDIT_VOTE_LIMIT, ANSWER_CAN_EDIT_VOTE_LIMIT,
	COMMENT_CAN_EDIT_TIME_LIMIT, COMMENT_CAN_EDIT_UPVOTE_LIMIT,
	QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT, QUESTION_CAN_DELETE_VOTE_LIMIT, 
	ANSWER_CAN_DELETE_VOTE_LIMIT, COMMENT_CAN_DELETE_UPVOTE_LIMIT
)


class CanEditQuestionMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		self.user, self.object = self.request.user, self.get_object()
		return self.user.can_edit_question(self.object)
		
	def get_permission_denied_message(self):
		# self.object will be set in the test_func
		# and the test_func is always called before this function
		question = self.object

		if self.user != question.poster:
			return _("You can only edit your own questions.")

		if question.vote_count > QUESTION_CAN_EDIT_VOTE_LIMIT or question.num_answers > QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT:
			return _(
				"You can only edit questions with less than {} votes(number of likes - number of dislikes) or less than {} answers. You may post a new question.".format(QUESTION_CAN_EDIT_VOTE_LIMIT, QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT)
			)
		return super().get_permission_denied_message()


class CanEditAnswerMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		self.user, self.object = self.request.user, self.get_object()
		return self.user.can_edit_answer(self.object)
		
	def get_permission_denied_message(self):
		answer = self.object

		if self.user != answer.poster:
			return _("You can only edit your own answers.")

		if answer.vote_count > ANSWER_CAN_EDIT_VOTE_LIMIT:
			return _(
				"You can only edit answers with less than {} votes(number of likes - number of dislikes). You may post a new answer if you have less than {} answers to this question.".format(ANSWER_CAN_EDIT_VOTE_LIMIT, MAX_ANSWERS_PER_USER_PER_QUESTION)
			)
		return super().get_permission_denied_message()


class CanEditCommentMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		self.user, self.object = self.request.user, self.get_object()
		return self.user.can_edit_comment(self.object)
		
	def get_permission_denied_message(self):
		comment = self.object

		if self.user != comment.poster:
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
	def test_func(self):
		self.user, self.object = self.request.user, self.get_object()
		return self.user.can_delete_question(self.object)

	def get_permission_denied_message(self):
		question, user = self.object, self.user

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
	def test_func(self):
		self.user, self.object = self.request.user, self.get_object()
		return self.user.can_delete_answer(self.object)
		
	def get_permission_denied_message(self):
		user, answer = self.user, self.object

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
	def test_func(self):
		self.user, self.object = self.request.user, self.get_object()
		return self.user.can_delete_comment(self.object)
		
	def get_permission_denied_message(self):
		user, comment = self.user, self.object

		if user.is_mod:
			return _("Moderators can delete only flagged comments.")

		if user != comment.poster:
			return _("You can only delete your own comments.")

		if comment.upvote_count > COMMENT_CAN_DELETE_UPVOTE_LIMIT:
			return _(
				"You can only delete comments with less than {} likes. This comment may help future users.".format(COMMENT_CAN_DELETE_UPVOTE_LIMIT)
			)
		return super().get_permission_denied_message()

