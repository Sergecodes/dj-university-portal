import os
from django.conf import settings
from django.core.files import File
from fpdf import FPDF


def generate_pdf(imagelist, gen_file_name, dir='media', gen_files_dir='past_papers'):
	"""
	Generate a pdf containing images in image_list and return a django File object pointing to the pdf. \n
	`image_list` is a list of the images \n
	`gen_file_name` name(without extension) of output file \n
	`dir` is the folder in BASE_DIR which contains upload_to directories) \n
	`files_dir` is the folder in `dir`(BASE_DIR/dir) where generated files should be stored
	"""
	
	pdf = FPDF()

	for image in imagelist:
		pdf.add_page()
		image_path = os.path.join(settings.BASE_DIR, dir, image.file.name)
		# w=210, h=297 is the standard for A4 sized pdfs
		# no height is set so that the original height of the image is maintained and the image isn't stretched vertically
		pdf.image(image_path, 0, 0, 210)
	output_file = os.path.join(settings.BASE_DIR, dir, gen_files_dir, gen_file_name + '.pdf')
	pdf.output(output_file, 'F')

	# return generated file's name (with extension)
	return gen_file_name + '.pdf'

