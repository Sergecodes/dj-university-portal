from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext_lazy as _

from flagging.models import Flag


def can_edit_item(user, item):
	"""Verify if user is permitted to edit item (lost/found item)"""
	return user.id == item.poster_id


class CanEditItemMixin(LoginRequiredMixin, UserPassesTestMixin):
	"""Custom mixin to ensure user is poster of item."""

	def test_func(self):
		# Permit access to only post owners 
		return can_edit_item(self.request.user, self.get_object())


def can_delete_item(user, item):
	"""Verify if user is permitted to delete item (lost/found item)"""
	if user.id == item.poster_id or user.is_staff:
		return True

	# if item is flagged moderator can delete it.
	if user.is_mod and Flag.objects.is_flagged(item):
		return True

	return False


class CanDeleteItemMixin(LoginRequiredMixin, UserPassesTestMixin):
	"""
	Custom mixin to ensure user is poster of item or staff.
	If user is moderator, he can delete the item only if it is `flagged`.
	"""
	# staff should be permitted to delete coz there may be some flag-worthy posts
	# that haven't yet been flagged...

	def test_func(self):
		return can_delete_item(self.request.user, self.get_object())

	def get_permission_denied_message(self):
		user = self.request.user

		if user.is_mod:
			return _("Moderators can only delete flagged posts.")

		if user.id != self.get_object().poster_id:
			return _("You can delete only items that were posted by you.")
			
		return super().get_permission_denied_message()
