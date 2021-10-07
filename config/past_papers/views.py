import django_filters as filters
import os
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect
from django.template.defaultfilters import slugify
from django.utils.decorators import method_decorator
from django.utils.translation import get_language, gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from functools import reduce

from core.constants import (
	PAST_PAPERS_UPLOAD_DIR, 
	PAST_PAPERS_PHOTOS_UPLOAD_DIR,
	PAST_PAPER_SUFFIX,
)
from core.mixins import GetObjectMixin, IncrementViewCountMixin 
from core.utils import generate_pdf, get_photos
from qa_site.models import Subject
from .forms import PastPaperForm, CommentForm
from .models import PastPaper, PastPaperPhoto, Subject


class PastPaperCreate(LoginRequiredMixin, CreateView):
	model = PastPaper
	form_class = PastPaperForm

	def get_form_kwargs(self, **kwargs):
		form_kwargs, request = super().get_form_kwargs(**kwargs), self.request
		photos_list = request.session.get(request.user.username + PAST_PAPER_SUFFIX, [])
		
		form_kwargs['initial_photos'] = get_photos(
			PastPaperPhoto, 
			photos_list, 
			PAST_PAPERS_PHOTOS_UPLOAD_DIR
		)
		return form_kwargs

	def post(self, request, *args, **kwargs):
		self.object, user = None, request.user
		form = self.get_form()
		photos_list = request.session.get(user.username + PAST_PAPER_SUFFIX, [])

		# these validations isn't done in the form's clean 
		# coz we won't have access to the request object to get the session
		file = request.FILES.get('file')

		if file and photos_list:
			form.add_error(None, ValidationError(_('Either upload a file or photo(s), not both.')))
		
		if not file and not photos_list:
			form.add_error(None, ValidationError(_('Upload a file or photo(s)')))

		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def form_valid(self, form):
		request = self.request
		self.object = form.save(commit=False)
		session, user = request.session, request.user
		past_paper = self.object
		past_paper.poster = user
		past_paper.language = get_language()
	
		# get list of photo names, remember photos are not compulsory, so use empty list as default
		photos_list = session.get(user.username + PAST_PAPER_SUFFIX, [])
		instance_list = []

		# create photo instances pointing to the pre-created photos 
		# recall that these photos are already in the file system
		for photo_name in photos_list:
			photo_path = os.path.join(PAST_PAPERS_PHOTOS_UPLOAD_DIR, photo_name)
			f = open(photo_path, 'rb')
			django_file = File(f)
			instance_list.append(PastPaperPhoto(file=django_file))
			f.close()

		instance_list = PastPaperPhoto.objects.bulk_create(instance_list)
		# point past_paper file to generated file
		past_paper.file.name = os.path.join(
			PAST_PAPERS_UPLOAD_DIR, generate_pdf(instance_list, slugify(past_paper.title))
		)
		past_paper.save()

		# remove photos list from session 
		request.session.pop(user.username + PAST_PAPER_SUFFIX, [])
		
		return redirect(past_paper)

		'''
		for photo_name in photos_list:
			photo = PastPaperPhoto()
			# path to file (relative path from MEDIA_ROOT)
			photo.file.name = os.path.join(PAST_PAPERS_PHOTOS_UPLOAD_DIR, photo_name)
			# since photo already has file, no file will be created, just the model instance.
			# save instance anyways, it may have some statistical/analytical uses in the future...
			photo.save()
			instance_list.append(photo)
		'''

		'''
		## this is the previous code for saving photos when the upload modal wasn't yet used
		# save photos to file system
		uploaded_photos = request.FILES.getlist('photos')
		# images will be cast to a list
		images = PastPaperPhoto.objects.bulk_create(
			[PastPaperPhoto(file=photo) for photo in uploaded_photos]
		)
		# point past_paper file to generated file
		past_paper.file.name = os.path.join(
			PAST_PAPERS_UPLOAD_DIR, generate_pdf(images, slugify(past_paper.title))
		)
		past_paper.save()
		'''


@method_decorator(login_required, name='post')
class PastPaperDetail(GetObjectMixin, IncrementViewCountMixin, DetailView):
	model = PastPaper
	context_object_name = 'past_paper'

	def post(self, request, *args, **kwargs):
		"""Handle submission of comments on past papers"""
		comment_form = CommentForm(request.POST)
		past_paper = get_object_or_404(PastPaper, id=request.POST.get('past_paper_id'))

		if comment_form.is_valid():
			comment = comment_form.save(commit=False)
			comment.past_paper = past_paper
			comment.poster = request.user
			comment.save()

		return redirect(past_paper.get_absolute_url())

	def get(self, request, *args, **kwargs):
		self.set_view_count()
		return super().get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		NUM_SIMILAR_PAPERS = 5
		COMMENTS_PER_PAGE = 2
		context = super().get_context_data(**kwargs)
		
		past_paper = self.object
		comments = past_paper.comments.select_related('poster').order_by('-posted_datetime')
		
		# get similar papers
		similar_papers = PastPaper.objects.filter(
			level=past_paper.level,
			type=past_paper.type,
			subject=past_paper.subject
		).only('title').order_by('-posted_datetime')[:NUM_SIMILAR_PAPERS]

		# paginate results
		paginator = Paginator(comments, COMMENTS_PER_PAGE)
		page_number = self.request.GET.get('page')
		# if page_number is None, the first page is returned
		page_obj = paginator.get_page(page_number)  

		context['comment_form'] = CommentForm()
		context['comments'] = comments
		context['similar_papers'] = similar_papers
		context['page_obj'] = page_obj
		# if more than one page is present, then the results are paginated
		context['is_paginated'] = paginator.num_pages > 1

		return context


class PastPaperFilter(filters.FilterSet):
	title = filters.CharFilter(label=_('Keywords'), method='filter_title')

	class Meta:
		model = PastPaper
		fields = ['school', 'subject', 'level', 'title', ]
	
	def filter_title(self, queryset, name, value):
		value_list = value.split()
		qs = queryset.filter(
			reduce(
				lambda x, y: x | y, 
				[Q(title__icontains=word) for word in value_list]
			)
		)
		
		return qs

class PastPaperList(FilterView):
	model = PastPaper
	filterset_class = PastPaperFilter
	template_name = 'past_papers/pastpaper_list.html'
	template_name_suffix = '_list'
	paginate_by = 8
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		subjects = Subject.objects.all().prefetch_related(
			Prefetch('past_papers', queryset=PastPaper.objects.all().only('id'))
		)

		# get number of papers that are registered under this subject
		num_papers = 0
		for subject in subjects:
			num_papers += subject.past_papers.count()

		context['subjects'] = Subject.objects.all()
		context['total_num_papers'] = num_papers
		context['levels'] = PastPaper.LEVELS
		
		return context
