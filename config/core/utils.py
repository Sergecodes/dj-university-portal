import os
import re
from django.apps import apps
from django.conf import settings
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from fpdf import FPDF
from functools import reduce
from PIL import Image, ImageDraw, ImageFont
from random import choice

BASE_DIR = settings.BASE_DIR
# get custom font here rather than loading it multiple times..
IMAGE_FONT = ImageFont.truetype(
	os.path.join(BASE_DIR, 'static/webfonts', 'ScheherazadeNew-Bold.ttf'),
	40
)


## CORE ##
def should_redirect(object, test_slug):
	"""
	Verify if an object should be redirected or not.
	Object is redirected if its slug is incorrect(not same as stored slug)
	Ex: user requests for item/3/incorrect-slug  => item/3/correct-slug
	"""

	if not hasattr(object, 'slug'):
		raise ValueError("Object must have a slug property")

	if object.slug != test_slug:
		return True
	else:
		return False


def insert_text_in_photo(image_path, text='CamerSchools.com'):
	"""Insert text on image"""
	img = Image.open(image_path)
	w, h = img.size

	# call draw method to insert 2D graphics in an image
	img_editable = ImageDraw.Draw(img)

	text_w, text_h = img_editable.textsize(text, IMAGE_FONT)
	x_pos, y_pos = h - text_h, w - text_w

	img_editable.text((x_pos, y_pos), text, (192, 192, 192), font=IMAGE_FONT)
	# save image and use same path so as to override it
	img.save(image_path)


def get_search_results(keyword_list, category=None):
	"""
	Search for the words in `keyword_list` in `category` label's model.
	`category`: App label or mnemonic..
	`keyword_list`: list of words to search with
	"""

	# import models here coz models won't be ready if the imports are placed at the top
	# since some functions here are used
	# in models and they need to be called when initializing the model
	LostItem = apps.get_model('lost_and_found.LostItem')
	FoundItem = apps.get_model('lost_and_found.FoundItem')
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


def generate_pdf(instance_list, gen_file_name, dir='media', gen_files_dir='past_papers'):
	"""
	Generate a pdf containing images in instance_list and return a django File object pointing to the pdf. Mostly(only) used with the past_papers app. \n
	`instance_list` is a list(or sequence) of the images(model instance used to store the image) eg. PastPaperPhoto \n
	`gen_file_name` name(without extension) of output file \n
	`dir` is the folder in BASE_DIR which contains upload_to directories) \n
	`gen_files_dir` is the folder in `dir`(BASE_DIR/dir) where generated files should be stored
	"""
	
	pdf = FPDF()

	for instance in instance_list:
		pdf.add_page()
		# path of image in storage
		image_path = os.path.join(BASE_DIR, dir, instance.file.name)
		# w=210, h=297 is the standard for A4 sized pdfs
		# no height is set so that the original height of the image is maintained and the image isn't stretched vertically which may cause vertical distortion
		pdf.image(image_path, 0, 0, 210)
	# todo in production, surely change this to aws bucket path
	output_file = os.path.join(BASE_DIR, dir, gen_files_dir, gen_file_name + '.pdf')
	pdf.output(output_file, 'F')

	# return generated file's name (with extension)
	return gen_file_name + '.pdf'


def is_mobile(request):
	"""Return `True` if the request comes from a mobile device and `False` otherwise."""
	MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

	if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
		return True

	return False


def get_photos(model, photos_name_list, dir):
	"""
	Return list of model photo instances from photos names. Mostly used in CreateView and UpdateView get_form_kwargs() to construct list of initial_photos of the template. \n
	`model` name of model containing the photo. eg ItemListingPhoto
	`photos_name_list` is the list of the names of the photos \n
	`dir` is the folder in MEDIA_ROOT where the photos are stored. eg. 'item_photos'. Can obtain some dir names from `core.constants.py`
	"""
	if not photos_name_list:
		print('No photos in list')
		return []
	
	photo_instances = []
	for photo_name in photos_name_list:
		photo = model()
		# path to file (relative path from MEDIA_ROOT)
		# each model should have a file field that holds the image.
		photo.file.name = os.path.join(dir, photo_name)
		photo.save()
		photo_instances.append(photo)

	print(photo_instances)
	return photo_instances


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


## LOST_AND_FOUND ##


## MARKETPLACE ##


## NOTIFICATIONS ##


## PAST_PAPERS ##


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
def get_random_profiles(count=7):
	"""
	Return a list of `count` randomly selected social profiles. 
	Only some particular fields for each profile is taken from the database.
	"""
	SocialProfile = apps.get_model('socialize', 'SocialProfile')
	random_profiles = []

	all_profiles = list(
		SocialProfile.objects.only(
			'user__username', 'user__site_points', 'gender'
		)
	)
	for i in range(count):
		random_profile = choice(all_profiles)

		# if user hasn't already been selected
		if random_profile not in random_profiles:
			random_profiles.append(random_profile)

	return random_profiles



## USERS ##
def get_edit_numbers_url(user):
	"""Get url to edit phone numbers for the given user."""
	return reverse('users:edit-profile', kwargs={'username': user.username}) + '#phoneSection'


def parse_email(email):
	"""
	Convert email to lowercase and replace `googlemail` to `gmail`
	Remember username@googlemail.com and username@gmail.com point to the same gmail account.
	see mailigen.com/blog/does-capitalization-matter-in-email-addresses/
	"""
	email = email.replace('googlemail', 'gmail')
	return email.lower()


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

