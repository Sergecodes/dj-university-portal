from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext_lazy as _

from flagging.models import Flag


def can_edit_listing(user, listing):
	"""Verify if user is permitted to edit listing"""
	return user.id == listing.poster_id


class CanEditListingMixin(LoginRequiredMixin, UserPassesTestMixin):
	"""Custom mixin to ensure user is poster of listing."""

	def test_func(self):
		return can_edit_listing(self.request.user, self.get_object())


def can_delete_listing(user, listing):
	"""Verify if user is permitted to delete listing"""
	# staff should be permitted to delete coz there may be some flag-worthy posts
	# that haven't yet been flagged...
	if user.id == listing.poster_id or user.is_staff:
		return True

	# if listing is flagged moderator can delete it.
	if user.is_mod and Flag.objects.is_flagged(listing):
		return True
	
	return False


class CanDeleteListingMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return can_delete_listing(self.request.user, self.get_object())

	def get_permission_denied_message(self):
		user = self.request.user

		if user.is_mod:
			return _("Moderators can only delete flagged posts.")

		if user != self.get_object().poster:
			# todo create 403 error template with message inserted..
			return _("You can delete only listings that were posted by you.")
			
		return super().get_permission_denied_message()
