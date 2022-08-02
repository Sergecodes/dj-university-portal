import cryptocode
from django.conf import settings
# from django.core.files.images import get_image_dimensions
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.http import require_GET, require_POST
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.templatetags.thumbnail import thumbnail_url

from core.constants import (
	MAX_LOST_ITEM_PHOTOS, PAST_PAPER_SUFFIX,
	ITEM_LISTING_SUFFIX, LOST_ITEM_SUFFIX,
	AD_LISTING_SUFFIX, REQUESTED_ITEM_SUFFIX,
	MAX_REQUESTED_ITEM_PHOTOS, MAX_ITEM_PHOTOS_LENGTH,
	LISTING_PHOTOS_UPLOAD_DIR, AD_PHOTOS_UPLOAD_DIR,
	LOST_ITEMS_PHOTOS_UPLOAD_DIR, REQUESTED_ITEMS_PHOTOS_UPLOAD_DIR,
	PAST_PAPERS_PHOTOS_UPLOAD_DIR, 
)
from core.models import Country
from core.utils import insert_text_in_photo
from lost_or_found.forms import LostItemPhotoForm
from marketplace.forms import (
	ItemListingPhotoForm as ItemPhotoForm,
	AdListingPhotoForm as AdPhotoForm
)
from past_papers.forms import PastPaperPhotoForm
from requested_items.forms import RequestedItemPhotoForm

USE_S3 = settings.USE_S3
STORAGE = import_string(settings.DEFAULT_FILE_STORAGE)()
SECRET_KEY = settings.SECRET_KEY
THUMBNAIL_ALIASES = settings.THUMBNAIL_ALIASES
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


class PhotoUploadView(View):
	# this isn't even required, if a method not defined in this class is used (eg. GET)
	# the request will fail.
	# also, these methods must be in lowercase apparently.
	# http_method_names = ['delete', 'post']

	def post(self, request, form_for):
		"""
		Called when a photo is uploaded. Checks for maximum number of photos are done where necessary.
		However, for minimum number of photos, checks will be done in the respective form's post method.
		"""

		# since it's an ajax view, if user isn't logged in, he will be redirected
		# but page won't be reloaded
		# so return json response if user is anonymous..
		if request.user.is_anonymous:
			return JsonResponse({
					'is_valid': False, 
					'error': _('User is not authenticated'), 
					'is_anonymous': True
				},
				status=401  # Unauthorized, anonymous user
			)

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
			image_obj, saved_photo_name = insert_text_in_photo(file, FORM_AND_UPLOAD_DIR[form_for]) 
			img_file = image_obj.file

			# if image has lesser dimensions than the thumbnail size(width + height)
			# use same image (use small thumb to generate thumbnail)
			thumb_dim = sum(THUMBNAIL_ALIASES['']['thumb']['size'])
			if img_file.width + img_file.height < thumb_dim:
				thumbnailer = get_thumbnailer(img_file)

				if form_for == 'past_paper':
					thumb_file = thumbnailer['pp_thumb']
				else:
					thumb_file = thumbnailer['sm_thumb']

				thumb_url = thumb_file.url
			else:
				if form_for == 'past_paper':
					thumb_url = thumbnail_url(img_file, 'pp_thumb') 
				else:
					thumb_url = thumbnail_url(img_file, 'thumb')

			## as of now, uploading a single file(photo) causes 3 requests to the storage.
			# inserting text in image causes 2(or 1?). 
			# the original file is saved after the text in inserted
			# before the thumbnail is generated and saved.
			# TODO find a way to generate the thumbnail without saving the original file in storage;
			# perhaps a byte string? does easy_thumbnails support this....

			photo_session_name = thumb_url.split('/')[-1]
			user_photos_list.append(photo_session_name)
			session[username + FORM_AND_SUFFIX[form_for]] = user_photos_list
			
			data = {
				'is_valid': True, 
				# 'url': STORAGE.url(saved_photo_name),
				# use thumbnail of file to minimize request latency
				# if user initially uploads say 3mb file, thats much. so use thumbnail instead.
				'url': thumb_url,

				# encrypt photo name before sending! why though ?!
				# also, encode url too to correctly parse signs such as plus and space that
				# could be in the cipher text. (see stackoverflow.com/q/66167067/querydict-in-django )
				## for some reason, urlencode(ciphertext) doesn't seem to work;
				# the encoding will be done using JS' encodeURIComponent on client side.
				'filename': cryptocode.encrypt(photo_session_name, SECRET_KEY)
			}

			return JsonResponse(data)

		# eg. when user submits wrong file type..
		else:
			print(form.errors)
			data = {
				'is_valid': False, 
				'error': form.errors.as_json()
				# 'error': _('Invalid file, upload a valid image(PNG or JPEG).')
			}

			return JsonResponse(data, status=400)

	def delete(self, request):
		"""Called when a photo is deleted. Removes photo from list of photos."""
		
		if request.user.is_anonymous:
			return JsonResponse({
					'deleted': False, 
					# 'error': _('User is not authenticated'), 
					'is_anonymous': True
				},
				status=401  # Unauthorized(Anonymous User)
			)
		
		encoded_photo_name = request.GET.get('photo_filename')
		form_for = request.GET.get('form_for')

		# in normal circumstances, this shouldn't be the case
		if not encoded_photo_name and not form_for:
			return JsonResponse(
				{'deleted': False, 'error': _('Invalid query params')},
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
		STORAGE.delete(decoded_photo_name)
		del user_photos_list[photo_index]
		session[username + FORM_AND_SUFFIX[form_for]] = user_photos_list

		return JsonResponse({'deleted': True})


@require_GET
def get_country_cities(request):
	"""Return the cities of a given country"""

	# no need to coerce, get_object_or_404 handles coercion
	country_pk = request.GET.get('country_id')

	if not country_pk:
		return JsonResponse({ 'cities': [] })

	country = get_object_or_404(Country, pk=country_pk)
	result = {
		# get id and name of each city in list
		'cities': list(country.cities.values('id', 'name'))
	}

	return JsonResponse(result)

