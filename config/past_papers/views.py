import django_filters as filters
import os
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import slugify
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView

from core.constants import PAST_PAPERS_UPLOAD_DIR
from core.utils import generate_pdf
from qa_site.models import Subject
from .forms import PastPaperForm, PastPaperPhotoForm, CommentForm
from .models import PastPaper, PastPaperPhoto, Subject


class PastPaperCreate(LoginRequiredMixin, CreateView):
	model = PastPaper
	form_class = PastPaperForm
	success_url = '/'

	def form_valid(self, form):
		request = self.request
		self.object = form.save(commit=False)
		past_paper = self.object
		past_paper.poster = request.user
		# past_paper.save()

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
		
		return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name='post')
class PastPaperDetail(DetailView):
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

		return HttpResponseRedirect(past_paper.get_absolute_url())

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
	title = filters.CharFilter(label=_('Keyword'), lookup_expr='icontains')

	class Meta:
		model = PastPaper
		fields = ['school', 'subject', 'level', 'title', ]

	@property
	def qs(self):
		parent = super().qs
		return parent.order_by('-posted_datetime')


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
