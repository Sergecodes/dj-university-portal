from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.http.response import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import View

from core.constants import MAX_LOST_ITEM_PHOTOS
from lost_and_found.forms import LostItemPhotoForm
from marketplace.forms import (
	ItemListingPhotoForm as ItemPhotoForm,
	AdListingPhotoForm as AdPhotoForm
)


class PhotoUploadView(LoginRequiredMixin, View):
	# def get(self, request):
		# use this view just to test the file upload functionality on a separate url
	# 	photos = ItemListingPhoto.objects.all()
	# 	context = {'photos': photos}
	# 	return render(request, 'core/photos_upload.html', context)

	def delete(self, request):
		"""Called when a photo is deleted. Removes photo from list of photos."""
		# Remember, when a photo is posted, the database instance is deleted but the photo isn't.
		# todo.. I have two options: 
			# 1. remove photo from frontend but allow in backend storage.
			# 2. find photo(perhaps by name) and actually remove it from backend storage. this will cause unneccessary load on server... and besides we can always periodically remove photos not attached to model instances using cron jobs or some packages.
		# I'll go with option 1 for now.

		# photo_id = request.GET.get('photo_id')
		# get_object_or_404(ItemListingPhoto, pk=photo_id).delete()
		# # todo also remove file from storage

		# remove photo from session. PS note that the photo will still stay in storage.
		photo_filename = request.GET.get('photo_filename')
		# print(photo_filename)

		# in normal circumstances, this shouldn't be the case
		if not photo_filename:
			return JsonResponse({'deleted': False})

		username, session = request.user.username, request.session
		user_photos_list = session.get(username)

		# remove photo title from user photos and update session
		try:
			photo_index = user_photos_list.index(photo_filename)
		except ValueError:
			# in normal circumstances, this shouldn't be the case
			return JsonResponse({'deleted': False, 'error': _('Photo not in list')})

		del user_photos_list[photo_index]
		session[username] = user_photos_list
		# print(user_photos_list)

		return JsonResponse({'deleted': True})


	def post(self, request, form_for):
		"""Called when a photo is uploaded."""
		if form_for == 'item_listing':
			form = ItemPhotoForm(request.POST, request.FILES)
		elif form_for == 'ad_listing':
			form = AdPhotoForm(request.POST, request.FILES)
		elif form_for == 'lost_item':
			form = LostItemPhotoForm(request.POST, request.FILES)
		else:
			# return HttpResponseBadRequest(_('Invalid value for form_for'))
			return JsonResponse({'is_valid': False, 'error': _('Unsupported form used.')})
		
		user, session = request.user, request.session
		username = user.username
		user_photos_list = session.get(username, [])

		# if lost item num_photos already at maximum 
		if form_for == 'lost_item' and len(user_photos_list) == MAX_LOST_ITEM_PHOTOS:
			return JsonResponse({'is_valid': False, 'error': _('Max number of photos attained')})

		# print(request.FILES)
		if form.is_valid():
			photo = form.save()
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
			data = {'is_valid': False, 'error': _('Form contains errors. Bizarre !')}

		return JsonResponse(data)

