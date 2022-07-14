from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext_lazy as _

from flagging.models import Flag


def can_edit_item(user, item):
	"""Verify if user is permitted to edit requested item"""
	return user.id == item.poster_id


def can_delete_item(user, item):
	"""Verify if user is permitted to delete a requested item"""
	if user.id == item.poster_id or user.is_staff:
		return True

	# if item is flagged moderator can delete it.
	# AnonymousUser has no attr is_mod
	if user.is_authenticated and user.is_mod and Flag.objects.is_flagged(item):
		return True

	return False


class CanEditRequestedItemMixin(LoginRequiredMixin, UserPassesTestMixin):
	
	def test_func(self):
		return can_edit_item(self.request.user, self.get_object())


class CanDeleteRequestedItemMixin(LoginRequiredMixin, UserPassesTestMixin):
	
	def test_func(self):
		return can_delete_item(self.request.user, self.get_object())	

	def get_permission_denied_message(self):
		user = self.request.user

		if user.is_mod:
			return _("Moderators can only delete flagged posts.")

		if user != self.get_object().poster:
			# todo create 403 error template with message inserted..
			return _("You can delete only items that were posted by you.")

		return super().get_permission_denied_message()
