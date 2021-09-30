from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext_lazy as _

from flagging.models import Flag


class CanEditListingMixin(LoginRequiredMixin, UserPassesTestMixin):
	"""Custom mixin to ensure user is poster of listing."""

	def test_func(self):
		# Permit access to only post owners 
		user = self.request.user
		self.object = self.get_object()
		return user == self.object.poster


class CanDeleteListingMixin(LoginRequiredMixin, UserPassesTestMixin):
	"""
	Custom mixin to ensure user is poster of listing or staff.
	If user is moderator, he can delete the listing only if it is `flagged`.
	"""
	# staff should be permitted to delete coz there may be some flag-worthy posts
	# that haven't yet been flagged...

	def test_func(self):
		self.object, user = self.get_object(), self.request.user
		listing = self.object
		
		if user == listing.poster or user.is_staff:
			return True

		# if listing is flagged moderator can delete it.
		if user.is_mod and Flag.objects.is_flagged(listing):
			return True

	def get_permission_denied_message(self):
		user = self.request.user

		if user.is_mod:
			return _("Moderators can only delete flagged posts.")

		if user != self.get_object().poster:
			# todo create 403 error template with message inserted..
			return _("You can delete only listings that were posted by you.")
			
		return super().get_permission_denied_message()
