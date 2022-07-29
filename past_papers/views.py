import django_filters as filters
from django_filters.views import FilterView
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.utils.text import slugify
from django.utils.translation import get_language, gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from functools import reduce

from core.constants import (
	PAST_PAPERS_UPLOAD_DIR, PAST_PAPER_SUFFIX,
	PAST_PAPERS_PHOTOS_UPLOAD_DIR,
)
from django.core.files.base import ContentFile
from core.mixins import GetObjectMixin, IncrementViewCountMixin
from core.utils import generate_past_papers_pdf, get_photos, should_redirect
from qa_site.models import Subject
from .forms import PastPaperForm, CommentForm
from .mixins import (
	can_delete_paper, CanDeletePastPaperMixin, 
	CanDeletePastPaperCommentMixin, CanEditPastPaperCommentMixin,
)
from .models import PastPaper, Comment

STORAGE = import_string(settings.DEFAULT_FILE_STORAGE)()


class PastPaperCreate(LoginRequiredMixin, CreateView):
	model = PastPaper
	form_class = PastPaperForm

	def get_form_kwargs(self, **kwargs):
		form_kwargs, request = super().get_form_kwargs(**kwargs), self.request
		user, session = request.user, request.session
		photos_list = session.get(user.username + PAST_PAPER_SUFFIX, [])
		
		form_kwargs['initial_photos'] = get_photos(photos_list, PAST_PAPERS_PHOTOS_UPLOAD_DIR)
		form_kwargs['country_or_code'] = session.get('country_code', user.country)
		return form_kwargs

	def post(self, request, *args, **kwargs):
		self.object, user = None, request.user
		form = self.get_form()
		photos_list = request.session.get(user.username + PAST_PAPER_SUFFIX, [])

		# these validations isn't done in the form's clean 
		# coz we won't have access to the request object to get the session
		file = request.FILES.get('file')
		
		if file and photos_list:
			form.add_error(
				None, 
				ValidationError(_('Either upload a file or photo(s), not both.'))
			)
		
		if not file and not photos_list:
			form.add_error(None, ValidationError(_('Upload a file or photo(s)')))

		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def form_valid(self, form):
		request = self.request
		past_paper = self.object = form.save(commit=False)
		session, user = request.session, request.user
		
		past_paper.poster = user
		past_paper.language = get_language()
	
		# get list of photo names, remember photos are not compulsory, 
		# so use empty list as default
		photos_list = session.get(user.username + PAST_PAPER_SUFFIX, [])
		
		if photos_list:
			# generate past paper from photos
			byte_str = generate_past_papers_pdf(photos_list)
			filename = slugify(past_paper.title)

			# save byte string to django file
			file = ContentFile(byte_str)
			pdf_name = STORAGE.save(PAST_PAPERS_UPLOAD_DIR + filename + '.pdf', file)
			
			# save file
			past_paper.file.name = pdf_name

			# remove photos list from session 
			request.session.pop(user.username + PAST_PAPER_SUFFIX, [])

		past_paper.save()
		return redirect(past_paper)


class PastPaperDelete(GetObjectMixin, CanDeletePastPaperMixin, DeleteView):
	model = PastPaper
	success_url = reverse_lazy('past_papers:past-paper-list')


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
			comment.original_language = get_language()
			comment.save()

		return redirect(past_paper.get_absolute_url())

	def get(self, request, *args, **kwargs):
		if should_redirect(object := self.get_object(), kwargs.get('slug')):
			return redirect(object, permanent=True)
		
		self.set_view_count()
		return super().get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		NUM_SIMILAR_PAPERS, COMMENTS_PER_PAGE = 5, 2
		user = self.request.user

		context = super().get_context_data(**kwargs)
		past_paper = self.object
		comments = past_paper.comments.select_related('poster') \
			.order_by('-posted_datetime')
		
		# get similar papers
		similar_papers = PastPaper.objects.filter(
			level=past_paper.level,
			type=past_paper.type,
			subject=past_paper.subject
		).exclude(id=past_paper.id).only('title').order_by('-posted_datetime')[:NUM_SIMILAR_PAPERS]

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
		context['can_delete_paper'] = False if user.is_anonymous else can_delete_paper(user, past_paper)

		return context


class PastPaperFilter(filters.FilterSet):
	title = filters.CharFilter(label=_('Keywords'), method='filter_title')

	class Meta:
		model = PastPaper
		fields = ['country', 'subject', 'level', 'title', ]
		
	def __init__(self, *args, **kwargs):
		# set label for fields,
		# this is to enable translation of labels.
		super().__init__(*args, **kwargs)
		self.filters['country'].label = _('Country')
		self.filters['subject'].label = _('Subject')
		self.filters['level'].label = _('Level')

	@property
	def qs(self):
		parent_qs = super().qs
		if country_code := self.request.session.get('country_code'):
			return parent_qs.filter(country__code=country_code)

		return parent_qs

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
	paginate_by = 7
	
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


## Past paper comment edit and delete views
class PastPaperCommentUpdate(GetObjectMixin, CanEditPastPaperCommentMixin, UpdateView):
	# set fields to update.
	# if you use the form_class attribute instead, 
	# you will manually need to save/update some fields
	fields = ['content']
	model = Comment
	template_name = 'past_papers/comment_edit.html'

	def get_success_url(self):
		return self.get_object().past_paper.get_absolute_url()

	def form_valid(self, form):
		if 'content' in form.changed_data:
			comment = form.save(commit=False)
			comment.update_language = get_language()
			comment.save()
			
		return redirect(self.get_success_url())


class PastPaperCommentDelete(GetObjectMixin, CanDeletePastPaperCommentMixin, DeleteView):
	model = Comment

	def get_success_url(self):
		return self.get_object().past_paper.get_absolute_url()


## Bookmarking
@login_required
@require_POST
def past_paper_bookmark_toggle(request):
	"""This view handles bookmarking for past papers"""
	user, POST = request.user, request.POST
	id, action = POST.get('id'), POST.get('action')
	past_paper = get_object_or_404(PastPaper, pk=id)

	# if vote is new (not removing bookmark)
	if action == 'bookmark':
		past_paper.bookmarkers.add(user)
		return JsonResponse({'bookmarked': True}, status=200)

	# if user is retracting bookmark
	elif action == 'recall-bookmark':
		past_paper.bookmarkers.remove(user)
		return JsonResponse({'unbookmarked': True}, status=200)
	else:
		return JsonResponse({'error': _('Invalid action')}, status=400)

