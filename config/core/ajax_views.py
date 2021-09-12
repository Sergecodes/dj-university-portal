from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.http.response import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import View

from core.constants import (
	MAX_LOST_ITEM_PHOTOS, PAST_PAPER_SUFFIX,
	ITEM_LISTING_SUFFIX, LOST_ITEM_SUFFIX,
	AD_LISTING_SUFFIX
)
from lost_and_found.forms import LostItemPhotoForm
from marketplace.forms import (
	ItemListingPhotoForm as ItemPhotoForm,
	AdListingPhotoForm as AdPhotoForm
)
from past_papers.forms import PastPaperPhotoForm


class PhotoUploadView(LoginRequiredMixin, View):
	def delete(self, request):
		"""Called when a photo is deleted. Removes photo from list of photos."""

		FORM_AND_SUFFIX = {
			'item_listing': ITEM_LISTING_SUFFIX,
			'ad_listing': AD_LISTING_SUFFIX,
			'lost_item': LOST_ITEM_SUFFIX,
			'past_paper': PAST_PAPER_SUFFIX
		}
		photo_filename = request.GET.get('photo_filename')
		form_for = request.GET.get('form_for')

		# in normal circumstances, this shouldn't be the case
		if not (photo_filename and form_for):
			return JsonResponse(
				{'deleted': False, 'error': _('Invalid GET params')},
				status=400  # BadRequest
			)
		
		username, session = request.user.username, request.session
		user_photos_list = session.get(username + FORM_AND_SUFFIX[form_for], [])

		# remove photo title from user photos and update session
		try:
			photo_index = user_photos_list.index(photo_filename)
		except ValueError:
			# in normal circumstances, this shouldn't be the case
			return JsonResponse(
				{'deleted': False, 'error': _('Photo not in list, bizarre')},
				status=400
			)

		del user_photos_list[photo_index]
		session[username + FORM_AND_SUFFIX[form_for]] = user_photos_list

		return JsonResponse({'deleted': True})


	def post(self, request, form_for):
		"""Called when a photo is uploaded."""

		FORM_AND_SUFFIX = {
			'item_listing': ITEM_LISTING_SUFFIX,
			'ad_listing': AD_LISTING_SUFFIX,
			'lost_item': LOST_ITEM_SUFFIX,
			'past_paper': PAST_PAPER_SUFFIX
		}

		if form_for == 'item_listing':
			form = ItemPhotoForm(request.POST, request.FILES)
		elif form_for == 'ad_listing':
			form = AdPhotoForm(request.POST, request.FILES)
		elif form_for == 'lost_item':
			form = LostItemPhotoForm(request.POST, request.FILES)
		elif form_for == 'past_paper':
			form = PastPaperPhotoForm(request.POST, request.FILES)
		else:
			# return HttpResponseBadRequest(_('Invalid value for form_for'))
			# BadRequest
			return JsonResponse({'is_valid': False}, status=400)
		
		username, session = request.user.username, request.session
		user_photos_list = session.get(username + FORM_AND_SUFFIX[form_for], [])

		# if lost item num_photos already at maximum 
		if form_for == 'lost_item' and len(user_photos_list) == MAX_LOST_ITEM_PHOTOS:
			return JsonResponse(
				{'is_valid': False, 'error': _('Maximum number of photos attained')},
				status=405  # NotAllowed
			)

		# print(request.FILES)
		# if upload was successful, add photo name to user session variable
		# we'll save the model instance (hence  storing the file) then later delete it
		if form.is_valid():
			photo = form.save()
			user_photos_list.append(photo.actual_filename)
			session[username + FORM_AND_SUFFIX[form_for]] = user_photos_list

			data = {
				'is_valid': True, 
				'id': photo.id, 
				'url': photo.file.url,
				'title': photo.title,
				'filename': photo.actual_filename  
			}
			
			# delete model instance but keep file(django doesn't delete the actual file) 
			# (# todo ensure this holds even after external packages are installed...)
			# this is so that when posting the overall form, the instances are recreated from the photos and there should be no duplicate instances
			photo.delete()

		# eg. when user submits wrong file type..
		else:
			data = {'is_valid': False, 'error': _('Invalid file type, upload a valid image.')}

		return JsonResponse(data)

