import os
import re
from django.apps import apps
from django.conf import settings
from django.urls import reverse
from fpdf import FPDF
from random import choice

BASE_DIR = settings.BASE_DIR


## CORE ##
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

