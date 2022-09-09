from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext_lazy as _

from core.constants import (
	QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT,
	QUESTION_CAN_EDIT_VOTE_LIMIT, QUESTION_CAN_DELETE_VOTE_LIMIT, 
	QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT, 
)


class CanEditQuestionMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		self.user, self.object = self.request.user, self.get_object()
		return self.user.can_edit_question(self.object)
		
	def get_permission_denied_message(self):
		# self.object will be set in the test_func
		# and the test_func is always called before this function
		question = self.object

		if self.user.id != question.poster_id:
			return _("You can only edit your own questions.")

		if question.vote_count > QUESTION_CAN_EDIT_VOTE_LIMIT or \
			question.num_answers > QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT:
			return _(
				"You can only edit questions with less than {} votes"
				"(number of likes - number of dislikes) or less than {} answers. \n "
				"You may post a new question.".format(
					QUESTION_CAN_EDIT_VOTE_LIMIT, QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT
				)
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

		if user.id != question.poster_id:
			return _("You can only delete your own questions.")

		if question.vote_count > QUESTION_CAN_DELETE_VOTE_LIMIT or question.num_answers > QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT:
			return _(
				"You can only delete questions with less than {} votes(number of likes - number of dislikes) or less than {} answers. \n This question may help future users.".format(QUESTION_CAN_DELETE_VOTE_LIMIT, QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT)
			)
		return super().get_permission_denied_message()

