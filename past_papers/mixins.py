from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext_lazy as _

from core.constants import (
	PAST_PAPER_COMMENT_CAN_EDIT_TIME_LIMIT, 
	PAST_PAPER_CAN_DELETE_TIME_LIMIT
)


def can_delete_paper(user, past_paper):
	"""Verify if user is permitted to delete past_paper"""
	# ensure, user calling this view is authed
	if user.is_anonymous:
		return False
	return user.can_delete_past_paper(past_paper)


def can_edit_comment(user, comment):
	"""Verify if user can edit a comment under a past paper"""
	if user.is_anonymous:
		return False
	return user.can_edit_past_paper_comment(comment)


def can_delete_comment(user, comment):
	"""Verify if user can delete a comment under a past paper"""
	if user.is_anonymous:
		return False
	return user.can_delete_past_paper_comment(comment)


class CanDeletePastPaperMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return can_delete_paper(self.request.user, self.get_object())

	def get_permission_denied_message(self):
		user, past_paper = self.request.user, self.object

		if user.is_mod:
			return _("Moderators can only delete flagged posts.")

		if user.id != past_paper.poster_id:
			return _("You can delete only past papers that were uploaded by you.")

		if not past_paper.is_within_delete_timeframe: 
			return _(
				# use str() to convert the timedelta object to a convenient value
				"You can't delete papers that are more than {} minutes old." \
					.format(str(PAST_PAPER_CAN_DELETE_TIME_LIMIT))
			)
			
		return super().get_permission_denied_message()


class CanEditPastPaperCommentMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return can_edit_comment(self.request.user, self.get_object())
		
	def get_permission_denied_message(self):
		# self.object will be set in the test_func
		# and the test_func is always called before this function
		comment = self.object

		if self.id != comment.poster_id:
			return _("You can only edit your own comments.")

		if not comment.is_within_edit_timeframe: 
			return _(
				# use str() to convert the timedelta object to a convenient value
				"You can't edit comments that are more than {} minutes old." \
					.format(str(PAST_PAPER_COMMENT_CAN_EDIT_TIME_LIMIT))
			)

		return super().get_permission_denied_message()


class CanDeletePastPaperCommentMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return can_delete_comment(self.request.user, self.get_object())

	def get_permission_denied_message(self):
		user, comment = self.request.user, self.object

		if user.is_mod:
			return _("Moderators can only delete flagged posts.")

		if user.id != comment.poster_id:
			return _("You can delete only your comments.")
			
		return super().get_permission_denied_message()


