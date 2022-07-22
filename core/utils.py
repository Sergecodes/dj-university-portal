import cryptocode
import os
import re
from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils.module_loading import import_string
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from fpdf import FPDF
from functools import reduce
from google.cloud import translate_v2 as translate
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from random import choice

from core.constants import PAST_PAPERS_PHOTOS_UPLOAD_DIR, VALID_IMAGE_FILETYPES

BASE_DIR = settings.BASE_DIR
MEDIA_ROOT = settings.MEDIA_ROOT
SECRET_KEY = settings.SECRET_KEY
# get custom font here rather than loading it multiple times..
IMAGE_FONT = ImageFont.truetype(
	os.path.join(BASE_DIR, 'core/static/webfonts', 'ScheherazadeNew-Bold.ttf'),
	40
)
STORAGE = import_string(settings.DEFAULT_FILE_STORAGE)()
# export GOOGLE_APPLICATION_CREDENTIALS='/home/sergeman/Downloads/camerschools-demo-c99628e30d95.json'


## CORE ##

def actual_filename(photo):
	"""
	Get file name of file with extension (not relative path from MEDIA_URL).
	`photo` should be in storage.
	If files have the same name, Django automatically appends a unique string to each file before storing.
	This property(function) returns the name of a file (on disk) with its extension.
	Ex. `Screenshot_from_2020_hGETyTo.png` or `Screenshot_from_2020.png`
	"""
	return os.path.basename(photo.name)


class PhotoModelMixin:
	"""Add additional methods to image-related models""" 

	@cached_property
	def actual_filename(self):
		return actual_filename(self.file)

	@cached_property
	def title(self):
		return self.actual_filename.split('.')[0]


class PhotoUploadMixin:
	"""
	Ensure valid photo format is uploaded(PNG/JPEG).
	Used in forms.
	"""

	def clean_file(self):
		photo = self.cleaned_data.get('file')

		if photo:
			format = Image.open(photo.file).format
			photo.file.seek(0)
			
			if format in VALID_IMAGE_FILETYPES:
				return photo
		
		self.add_error('file', _('Invalid file format, only JPEG/PNG are permitted'))


def translate_text(text, target):
	"""
	Translates text into the target language.
	Target must be an ISO 639-1 language code.
	See https://g.co/cloud/translate/v2/translate-reference#supported_languages
	"""
	translate_client = translate.Client()

	# text can also be a sequence of strings, in which case
	# this method will return a sequence of results for each text.
	result = translate_client.translate(text, target_language=target)

	# result will be a dict containing keys 
	# `input`, `translatedText`, `detectedSourceLanguage`
	return result


def should_redirect(object, test_slug):
	"""
	Verify if an object should be redirected or not.
	Object is redirected if its slug is incorrect(not same as stored slug)
	Ex: user requests for item/3/incorrect-slug  => item/3/correct-slug.
	This will enable showing(redirecting to) the correct id and slug in the url.
	"""

	if not hasattr(object, 'slug'):
		raise ValueError("Object must have a slug property")

	if object.slug != test_slug:
		return True
	else:
		return False


def insert_text_in_photo(photo, save_dir, text='Camerschools.com'):
	"""Insert text on image and save"""
	img = Image.open(photo)
	w, h = img.size

	# convert image to RGB (such as grayscale images)
	img = img.convert('RGB')

	# call draw method to insert 2D graphics in an image
	# this will return an error if image is grayscale.
	# see stackoverflow.com/q/39080087/pillow-strange-behavior-using-draw-rectangle/
	img_editable = ImageDraw.Draw(img)
	
	img_editable = ImageDraw.Draw(img)
	text_w, text_h = img_editable.textsize(text, IMAGE_FONT)

	# get cartesian position where to insert text
	# use (image_ord - text_ord) as offset before manipulating the ordinate in question
	# this will insert the text at bottom right corner
	x_pos, y_pos = (w - text_w) - 15, (h - text_h) - 15
	img_editable.text((x_pos, y_pos), text, (254, 192, 14), font=IMAGE_FONT)

	## convert PIL image to django-compatible file object and save
	# img.show()
	img_io = BytesIO()

	# our pdf file generator(FPDF) only supports png files from remote location(via url)
	# hence if photo is past paper, store as png
	if save_dir == PAST_PAPERS_PHOTOS_UPLOAD_DIR:
		img.save(img_io, format='PNG')
	else:
		img.save(img_io, format=photo.image.format)

	# create a new django file-like object that can be used
	img_file = ContentFile(img_io.getvalue())

	valid_name = STORAGE.get_valid_name(photo.name)

	# rename extension of past paper photo file
	# this name will be in the form 'past_paper_photos/filename.png'
	if save_dir == PAST_PAPERS_PHOTOS_UPLOAD_DIR:
		valid_name = valid_name.replace(valid_name.split('.')[-1], 'png')

	# store saved file in a model object
	saved_file_name = STORAGE.save(save_dir + valid_name, img_file)
	ImageHolder = apps.get_model('core.ImageHolder')
	image = ImageHolder()
	image.file = saved_file_name
	image.save()
	
	return image, saved_file_name


def get_minutes(time_d):
	"""Return the number of minutes of the timedelta object"""
	return (time_d.seconds // 60) % 60


def get_search_results(keyword_list, category=None):
	"""
	Search for the words in `keyword_list` in `category` label's model.
	`category`: App label or mnemonic..
	`keyword_list`: list of words to search with
	"""

	# import models here coz models won't be ready if the imports are placed at the top
	# since some functions here are used
	# in models and they need to be called when initializing the model
	LostItem = apps.get_model('lost_or_found.LostItem')
	FoundItem = apps.get_model('lost_or_found.FoundItem')
	ItemListing = apps.get_model('marketplace.ItemListing')
	AdListing = apps.get_model('marketplace.AdListing')
	AcademicQuestion = apps.get_model('qa_site.AcademicQuestion')
	SchoolQuestion = apps.get_model('qa_site.SchoolQuestion')
	PastPaper = apps.get_model('past_papers.PastPaper')
	RequestedItem = apps.get_model('requested_items.RequestedItem')

	# don't fret, querysets are lazily evaluated.
	SEARCH_RESULTS = {
		## lost and found app
		'lost_items': LostItem.objects.filter(
				reduce(
					lambda x, y: x | y, 
					[Q(item_lost__icontains=word) for word in keyword_list]
				)
			).only('item_lost'),
		'found_items': FoundItem.objects.filter(
				reduce(
					lambda x, y: x | y, 
					[Q(item_found__icontains=word) for word in keyword_list]
				)
			).only('item_found'),
		
		## marketplace app
		'item_listings': ItemListing.objects.filter(
				reduce(
					lambda x, y: x | y, 
					[Q(title__icontains=word) for word in keyword_list]
				)
			).only('title'),
		'ad_listings': AdListing.objects.filter(
				reduce(
					lambda x, y: x | y, 
					[Q(title__icontains=word) for word in keyword_list]
				)
			).only('title'),

		## past papers app
		'past_papers': PastPaper.objects.filter(
				reduce(
					lambda x, y: x | y, 
					[Q(title__icontains=word) for word in keyword_list]
				)
			).only('title'),

		## qa_site app
		'academic_questions': AcademicQuestion.objects.filter(
				reduce(
					lambda x, y: x | y, 
					[Q(title__icontains=word) for word in keyword_list]
				)
			).only('title'),
		# school questions are generally short, so this query shouldn't hurt that much
		'school_questions': SchoolQuestion.objects.filter(
				reduce(
					lambda x, y: x | y, 
					[Q(content__icontains=word) for word in keyword_list]
				)
			).only('content'),

		## requested_items app
		'requested_items': RequestedItem.objects.filter(
				reduce(
					lambda x, y: x | y, 
					[Q(item_requested__icontains=word) for word in keyword_list]
				)
			).only('item_requested'),
	}

	# get total results and count if no category was passed
	if not category:
		results_count = {
			'lost_items': SEARCH_RESULTS['lost_items'].count(),
			'found_items': SEARCH_RESULTS['found_items'].count(),
			'item_listings': SEARCH_RESULTS['item_listings'].count(),
			'ad_listings': SEARCH_RESULTS['ad_listings'].count(),
			'past_papers': SEARCH_RESULTS['past_papers'].count(),
			'academic_questions': SEARCH_RESULTS['academic_questions'].count(),
			'school_questions': SEARCH_RESULTS['school_questions'].count(),
			'requested_items': SEARCH_RESULTS['requested_items'].count(),
		}

		total_count = 0
		counts = results_count.values()

		for count in counts:
			total_count += count

		return (SEARCH_RESULTS, results_count, total_count)

	# results and count if category was passed
	results = SEARCH_RESULTS[category]
	return (results, results.count())


def is_mobile(request):
	"""Return `True` if the request comes from a mobile device and `False` otherwise."""
	MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

	if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
		return True

	return False


def get_photos(photos_name_list, dir):
	"""
	Return list of aws photo urls. Mostly used in CreateView and UpdateView 
	get_form_kwargs() to construct list of initial_photos of the template. \n
	`photos_name_list` is the list of the names of the photos obtained from the session \n
	`dir` is the folder in s3 bucket where the photos are stored. eg. 'item_photos'. 
	Can obtain some dir names from `core.constants.py`
	"""
	if not photos_name_list:
		# print('No photos in list')
		return []

	photos_info = []
	for photo_name in photos_name_list:
		# prints the path of the file eg. (ad_photos/filename.jpg)
		file_path = os.path.join(dir, photo_name)
		photos_info.append({
			'url': STORAGE.url(file_path),
			# this is the format of the file name expected in the upload view..
			'filename': cryptocode.encrypt(photo_name, SECRET_KEY)
		})

	return photos_info


def get_label(category):
	"""
	Used in search results to print an app label name for the category.
	Ex. 'ad_listings' => 'Ad Listings'
	"""
	# do this instead of using a more generic method such as `category.title().replace('_', ' ')`
	# coz we need the labels translated.
	label = ''

	if category == 'ad_listings':
		label = _('Adverts')
	elif category == 'item_listings':
		label = _('Items for Sale')
	elif category == 'requested_items':
		label = _('Requested Items')
	elif category == 'past_papers':
		label = _('Past Papers')
	elif category == 'lost_items':
		label = _('Lost Items')
	elif category == 'found_items':
		label = _('Found Items')
	elif category == 'school_questions':
		label = _('School-Based Questions')
	elif category == 'academic_questions':
		label = _('Academic Questions')
	else:
		raise ValueError("Category is invalid")

	return label


## FLAGGING ##


## lost_or_found ##


## MARKETPLACE ##


## NOTIFICATIONS ##


## PAST_PAPERS ##
def generate_past_papers_pdf(file_names):
	"""
	Generate a pdf containing images in file_names and return a django File object 
	pointing to the pdf. \n
	`file_names` is a list(or sequence) of the names of the files in s3 bucket; 
	generally obtained from the session. \n
	"""

	## The library FPDF only supports png images from remote locations.
	
	pdf = FPDF()
	if settings.USE_S3:
		image_urls = [STORAGE.url(PAST_PAPERS_PHOTOS_UPLOAD_DIR + name) for name in file_names]
	else:
		# Use full file location
		image_urls = [
			os.path.join(BASE_DIR, MEDIA_ROOT, PAST_PAPERS_PHOTOS_UPLOAD_DIR, name) 
			for name in file_names
		]

	# all files are stored as png so convert any 
	for url in image_urls:
		pdf.add_page()
		# w=210, h=297 is the standard for A4 sized pdfs
		# no height is set so that the original height of the image is maintained 
		# and the image isn't stretched vertically which may cause vertical distortion
		pdf.image(url, 0, 0, 210)

	# output_file = os.path.join(gen_files_dir, gen_file_name + '.pdf')
	# pdf.output(output_file, 'S')

	# return pdf as string(buffer)
	return pdf.output(dest='S').encode('latin-1')


## QA_SITE ##
def get_usernames_from_comment(comment, post_type):
	"""Get the usernames of all mentioned users in a comment"""
	# post_type is in {'question', 'answer'}
	# user should have at least comment under post. 
	# eg if user was mentioned under answer, for the user to be notified, 
	# he should have at least one comment under the answer.
	pass


## REQUESTED_ITEMS ##


## SOCIALIZE ##
def get_random_profiles(count=7, current_user=None):
	"""
	Return a list of `count` randomly selected social profiles. 
	Only some particular fields for each profile is taken from the database.
	"""
	SocialProfile = apps.get_model('socialize', 'SocialProfile')
	random_profiles = []
	
	# Exclude current user from list
	if current_user:
		qs = SocialProfile.objects.exclude(user_id=current_user.id) \
			.only('user__username', 'user__site_points', 'gender')
	else:
		qs = SocialProfile.objects.only(
			'user__username', 'user__site_points', 'gender'
		)
		
	if qs.count() != 0:
		all_profiles = list(qs)

		# complexity of this is currently O(n^2) in worst-case
		# though in reality it's amortized. since the length of the 
		# list(random_profiles) is initially empty then increases progressively
		# we get sum of (n * n-1 * n-2 ...) in opposite direction of course.
		# this is equivalent to n(n-1)/2 hence O(n^2)
		for i in range(count):
			random_profile = choice(all_profiles)

			# if user hasn't already been selected
			if random_profile not in random_profiles:
				random_profiles.append(random_profile)

			# else if user has been selected, do nothing...
			# however the likelyhood of this happening is slim
			# (especially if the initial list is large),
			# except if there are just a few elements in the initial list
			else:
				pass

	return random_profiles



## USERS ##
def get_edit_profile_url(user):
	"""Get url to edit profile for the given user."""
	return reverse('users:edit-profile', kwargs={'username': user.username})
	# return reverse('users:edit-profile', kwargs={'username': user.username}) + '#phoneSection'


def parse_full_name(full_name):
	"""
	Ensure full names are separated only with one space. 
	eg. 'John     Wick' => 'John Wick'
	"""
	# get list of names
	names_list = full_name.split()
	parsed_name = ' '.join(names_list)
	
	return parsed_name


def parse_phone_number(tel):
	"""
	Appropriately print a phone number.
	For an odd number, separate figures before printing.
	For an even number, return same number.
	Number should normally be odd.(like 6 51 20 98 98)
	e.g. 651234566(odd number) should return 6 51 23 45 66
	"""
	# if number is even, return it
	if len(tel) % 2 == 0:
		return tel
	
	# if number is odd, stylize it.
	result = tel[0]
	n = len(tel)

	for i in range(1, n, 2):
		temp = tel[i] + tel[i+1]
		result = result + ' ' + temp
	
	return result




# def comma_splitter(tag_string):
# 	"""
# 	Split tags on comma and convert to lowercase, then return list of tag names.
# 	It's used by django-taggit to parse tags. 
# 	- see django-taggit docs on using a custom tag string parser
# 	"""
# 	tag_list = tag_string.split(',')
# 	result_list = []

# 	for tag in tag_list:
# 		# strip() removes white space before/after a string 
# 		# and returns the result
# 		if stripped := tag.strip():
# 			result_list.append(stripped.lower())
	
# 	return result_list


# def comma_joiner(tags):
# 	"""
# 	Convert Tag instances to string; 
# 	Used by django-taggit.
# 	"""
# 	return ', '.join([tag.name for tag in tags])

