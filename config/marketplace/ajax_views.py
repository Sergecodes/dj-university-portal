from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from .forms import (
	ItemListingPhotoForm as ItemPhotoForm
)
from .models import (
	ItemCategory, 
	ItemListingPhoto
)


@login_required
def get_item_sub_categories(request):
	"""Return the sub categories of a given item category via ajax"""

	# no need to coerce, get_object_or_404 handles coercion
	category_pk = request.GET.get('category_id')  

	if not category_pk:
		return JsonResponse({'sub_categories': []})

	category = get_object_or_404(ItemCategory, pk=category_pk)
	result = {
		# get id and name of each sub category in list
		'sub_categories': list(category.sub_categories.values('id', 'name'))
	}

	return JsonResponse(result)


class PhotoUploadView(LoginRequiredMixin, View):
	# def get(self, request):
		# use this view just to test the file upload functionality on a separate url
	# 	photos = ItemListingPhoto.objects.all()
	# 	context = {'photos': photos}
	# 	return render(request, 'marketplace/photos_upload.html', context)

	def delete(self, request):
		"""Called when a photo is deleted."""
		# Remember, when a photo is posted, the database instance is deleted but the photo isn't.
		# todo.. I have two options: 
			# 1. remove photo from frontend but allow in backend storage.
			# 2. find photo(perhaps by name) and actually remove it from backend storage. this will cause unneccessary load on server... and besides we can always periodically remove photos not attached to model instances using cron jobs or some packages.
		# I'll go with option 1 for now.

		# photo_id = request.GET.get('photo_id')
		# get_object_or_404(ItemListingPhoto, pk=photo_id).delete()
		# # todo also remove file from storage

		# remove photo from session PS note that the photo will still stay in storage.
		photo_filename = request.GET.get('photo_filename')
		# print(photo_filename)

		username, session = request.user.username, request.session
		user_photos_list = session.get(username)
		# remove photo title from user photos and update session
		photo_index = user_photos_list.index(photo_filename)
		del user_photos_list[photo_index]
		session[username] = user_photos_list

		# print(user_photos_list)

		return JsonResponse({'deleted': True})

	def post(self, request):
		"""Called when a photo is uploaded."""
		form = ItemPhotoForm(request.POST, request.FILES)
		
		# print(request.FILES)
		if form.is_valid():
			photo = form.save()
			user, session = request.user, request.session
			username = user.username

			user_photos_list = session.get(username, [])
			user_photos_list.append(photo.actual_filename)
			session[username] = user_photos_list
			# print(session[username])

			data = {
				'is_valid': True, 
				'id': photo.id, 
				'url': photo.file.url,
				'title': photo.title,
				'filename': photo.actual_filename  
			}
			
			# delete model instance but keep file (# todo ensure this holds even after external packages are installed...)
			# this is so that when posting the overall form, the instances are recreated from the photos and there should be no duplicate instances
			photo.delete()  
		else:
			data = {'is_valid': False}

		return JsonResponse(data)

