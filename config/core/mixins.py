"""Site-wide mixins"""
from django.db.models import F

from socialize.models import SocialProfile


class GetObjectMixin:
	"""
	Cache object so as to prevent hitting database multiple times.
	Use this mixin in views that have UserPassesTestMixin to prevent multiple database fetches
	when doing `self.get_object()`
	"""

	def get_object(self):
		if not hasattr(self, '_object'):
			self._object = super().get_object()
			
		return self._object


class IncrementViewCountMixin:
	"""
	Increment the view_count of an object when it is been accesses.
	view_count is initially 0, and when the poster of an object accesses it, 
	its view_count isn't modified.
	"""
	
	def set_view_count(self):
		"""
		Set the view_count of the object. 
		Ensure objects calling this method have a view_count attribute
		"""
		object, request = self.get_object(), self.request

		if not hasattr(object, 'view_count'):
			raise ValueError("The object calling this method doesn't have a view_count attribute")

		# if SocialProfile model
		# (remember these objects don't have a poster property)
		# use their user attribute as poster..
		# views have a model property
		if self.model == SocialProfile:
			owner_id = object.user_id
		else:
			owner_id = object.poster_id

		# if user is not the poster of this post
		if request.user.id != owner_id:
			object.view_count = F('view_count') + 1
			object.save(update_fields=['view_count'])

			# now refresh object(get object) so as to get object with computed view_count
			# if you don't do this, view_count will be `F('view_count')+1`
			object.refresh_from_db()


