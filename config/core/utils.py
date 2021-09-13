import os
import re
from django.conf import settings
from django.core.files import File
from fpdf import FPDF

BASE_DIR = settings.BASE_DIR


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

