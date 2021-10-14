import cryptocode
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views import View

from core.constants import (
	MAX_LOST_ITEM_PHOTOS, PAST_PAPER_SUFFIX,
	ITEM_LISTING_SUFFIX, LOST_ITEM_SUFFIX,
	AD_LISTING_SUFFIX, REQUESTED_ITEM_SUFFIX,
	MAX_REQUESTED_ITEM_PHOTOS, MAX_ITEM_PHOTOS_LENGTH,
	LISTING_PHOTOS_UPLOAD_DIR, AD_PHOTOS_UPLOAD_DIR,
	LOST_ITEMS_PHOTOS_UPLOAD_DIR, REQUESTED_ITEMS_PHOTOS_UPLOAD_DIR,
	PAST_PAPERS_PHOTOS_UPLOAD_DIR, 
)
from core.utils import insert_text_in_photo
from core.storage_backends import PublicMediaStorage
from lost_and_found.forms import LostItemPhotoForm
from marketplace.forms import (
	ItemListingPhotoForm as ItemPhotoForm,
	AdListingPhotoForm as AdPhotoForm
)
from past_papers.forms import PastPaperPhotoForm
from requested_items.forms import RequestedItemPhotoForm


SECRET_KEY = settings.SECRET_KEY
FORM_AND_SUFFIX = {
	'item_listing': ITEM_LISTING_SUFFIX,
	'ad_listing': AD_LISTING_SUFFIX,
	'lost_item': LOST_ITEM_SUFFIX,
	'past_paper': PAST_PAPER_SUFFIX,
	'requested_item': REQUESTED_ITEM_SUFFIX
}
FORM_AND_UPLOAD_DIR = {
	'item_listing': LISTING_PHOTOS_UPLOAD_DIR,
	'ad_listing': AD_PHOTOS_UPLOAD_DIR,
	'lost_item': LOST_ITEMS_PHOTOS_UPLOAD_DIR,
	'past_paper': PAST_PAPERS_PHOTOS_UPLOAD_DIR,
	'requested_item': REQUESTED_ITEMS_PHOTOS_UPLOAD_DIR
}


class PhotoUploadView(LoginRequiredMixin, View):
	# this isn't even required, if a method not defined in this class is used (eg. GET)
	# the request will fail.
	# also, these methods must be in lowercase apparently.
	# http_method_names = ['delete', 'post']

	def post(self, request, form_for):
		"""
		Called when a photo is uploaded. Checks for maximum number of photos are done where necessary.
		However, for minimum number of photos, checks will be done in the respective form's post method.
		"""

		if form_for == 'item_listing':
			form = ItemPhotoForm(request.POST, request.FILES)
		elif form_for == 'ad_listing':
			form = AdPhotoForm(request.POST, request.FILES)
		elif form_for == 'lost_item':
			form = LostItemPhotoForm(request.POST, request.FILES)
		elif form_for == 'past_paper':
			form = PastPaperPhotoForm(request.POST, request.FILES)
		elif form_for == 'requested_item':
			form = RequestedItemPhotoForm(request.POST, request.FILES)
		else:
			return JsonResponse({'is_valid': False, 'error': _('Unsupported form')}, status=400)
		
		username, session = request.user.username, request.session
		user_photos_list = session.get(username + FORM_AND_SUFFIX[form_for], [])

		# if item listing num_photos already at maximum
		if form_for == 'item_listing' and len(user_photos_list) == MAX_ITEM_PHOTOS_LENGTH:
			return JsonResponse(
				{'is_valid': False, 'error': _('Maximum number of photos attained')},
				status=403  # Forbidden
			)

		# if lost item num_photos already at maximum 
		if form_for == 'lost_item' and len(user_photos_list) == MAX_LOST_ITEM_PHOTOS:
			return JsonResponse(
				{'is_valid': False, 'error': _('Maximum number of photos attained')},
				status=403  # Forbidden
			)

		# if requested item num_photos already at maximum 
		if form_for == 'requested_item' and len(user_photos_list) == MAX_REQUESTED_ITEM_PHOTOS:
			return JsonResponse(
				{'is_valid': False, 'error': _('Maximum number of photos attained')},
				status=403  # Forbidden
			)


		if form.is_valid():
			file = request.FILES['file']
			# insert site url as watermark on photo
			# this name is a path to the file. eg. ad_photos/filename.png
			# all files uploaded will be in a directory.
			saved_photo_name = insert_text_in_photo(file, FORM_AND_UPLOAD_DIR[form_for]) 

			# convert name to valid storage name and store in session
			storage = PublicMediaStorage()
			# this name will be in the form 'filename.jpg'
			photo_session_name = saved_photo_name.split('/')[1]
			user_photos_list.append(photo_session_name)
			session[username + FORM_AND_SUFFIX[form_for]] = user_photos_list
			
			data = {
				'is_valid': True, 
				'url': storage.url(saved_photo_name),
				# encrypt photo name before sending!
				'filename': cryptocode.encrypt(photo_session_name, SECRET_KEY)
			}

		# eg. when user submits wrong file type..
		else:
			data = {
				'is_valid': False, 
				'error': _('Invalid file, upload a valid image.')
			}

		return JsonResponse(data)


	def delete(self, request):
		"""Called when a photo is deleted. Removes photo from list of photos."""
		encoded_photo_name = request.GET.get('photo_filename')
		form_for = request.GET.get('form_for')

		# in normal circumstances, this shouldn't be the case
		if not (encoded_photo_name and form_for):
			return JsonResponse(
				{'deleted': False, 'error': _('Invalid GET params')},
				status=400  # BadRequest
			)
		
		username, session = request.user.username, request.session
		user_photos_list = session.get(username + FORM_AND_SUFFIX[form_for], [])

		## delete photo and update session
		# decrypt() returns False if decryption failed
		# remember it will be in the form 'filename.jgp'...
		decoded_photo_name = cryptocode.decrypt(encoded_photo_name, SECRET_KEY)

		if not decoded_photo_name:
			return JsonResponse(
				{'deleted': False, 'error': _('Invalid string')},
				status=400
			)

		try:
			photo_index = user_photos_list.index(decoded_photo_name)
		# if decoded_photo_name is not in list(user_photos_list).
		# in normal circumstances, this shouldn't be the case
		# except if user has modified encoded string...
		except ValueError:
			return JsonResponse(
				{'deleted': False, 'error': _('Photo is not in list.')},
				status=400
			)

		# delete file from storage and remove its entry from session
		storage = PublicMediaStorage()
		storage.delete(decoded_photo_name)
		del user_photos_list[photo_index]
		session[username + FORM_AND_SUFFIX[form_for]] = user_photos_list

		return JsonResponse({'deleted': True})
