"""Site-wide mixins"""
from django.db.models import F

# from socialize.models import SocialProfile


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
	Increment the view_count of an object when it is been accessed.
	Use in get requests.
	"""
	
	def set_view_count(self):
		"""
		Set the view_count of the object. 
		Ensure objects calling this method have a view_count attribute
		"""
		object, request = self.get_object(), self.request

		if not hasattr(object, 'view_count'):
			raise ValueError("The object calling this method doesn't have a view_count attribute")

		prev_count = object.view_count
		object.view_count = F('view_count') + 1
		object.save(update_fields=['view_count'])

		# Normally, if we want to access the F-modified view_count field above in the future, 
		# it needs to be reloaded from the database(eg using object.refresh_from_db()).
		# To prevent this reload, set the view_count to the incremented value, but don't save it.
		# And since this mixin is used only in get request, we are sure no saving will be done.
		object.view_count = prev_count + 1

		# # if SocialProfile model
		# # (remember these objects don't have a poster property)
		# # use their user attribute as poster..
		# # views have a model property
		# if self.model == SocialProfile:
		# 	owner_id = object.user_id
		# else:
		# 	owner_id = object.poster_id

		# # if user is not the poster of this post
		# if request.user.id != owner_id:
		# 	object.view_count = F('view_count') + 1
		# 	object.save(update_fields=['view_count'])

		# 	# now refresh object(get object) so as to get object with computed view_count
		# 	# if you don't do this, view_count will be `F('view_count')+1`
		# 	object.refresh_from_db()


