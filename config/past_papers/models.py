from django.contrib.auth import get_user_model
from django.db import models

from core.constants import PAST_PAPERS_UPLOAD_DIRECTORY, PAST_PAPERS_PHOTOS_UPLOAD_DIRECTORY
from marketplace.models import Institution
from qa_site.models import Subject
from users.models import get_dummy_user


class File(models.Model):
	title = models.CharField(max_length=255) 
	upload_datetime = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		if not self.id:
			# get file_name (here, file name is the name of the file as uploaded by user)
			file_name = self.file.name
			# get just file name from name and extension combination
			short_name = file_name.split('.')[0]
			self.title = short_name
		super().save(*args, **kwargs)

	class Meta:
		abstract = True

 
class PastPaperPhoto(File):
	# name of photo(without extension) as uploaded by user
	file = models.ImageField(upload_to=PAST_PAPERS_PHOTOS_UPLOAD_DIRECTORY)
	past_paper = models.ForeignKey(
		'PastPaper',
		on_delete=models.CASCADE,
		related_name='photos',
		related_query_name='photo',
		null=True, blank=True
	)


class PastPaper(models.Model):
	"""Official past papers and papers for revision"""
	title = models.CharField(max_length=255, blank=True, null=True)
	# used for pdf files
	file = models.FileField(null=True, blank=True, upload_to=PAST_PAPERS_UPLOAD_DIRECTORY)
	poster = models.ForeignKey(
		get_user_model(),
		on_delete=models.SET(get_dummy_user),
		related_name="past_papers",
		related_query_name="past_paper"
	) 
	# should be nullable..
	school = models.ForeignKey(
		Institution,
		on_delete=models.SET_NULL,
		related_name="past_papers",
		related_query_name="past_paper",
		null=True, blank=True
	)
	# nullable for subjects that aren't present(yet...)
	subject = models.ForeignKey(
		Subject,
		on_delete=models.PROTECT,
		related_name="past_papers",
		related_query_name="past_paper",
		null=True, blank=True
	)
	posted_datetime = models.DateTimeField(auto_now_add=True)
	# those with null=True will be considered as revision papers..
	written_date = models.DateField(null=True, blank=True)  # when the past paper was written..

	#todo add class(niveau.)	
