import django_filters as filters
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView

from qa_site.models import Subject
from .forms import PastPaperForm, PastPaperPhotoForm
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
		past_paper.save()

		uploaded_photos = request.FILES.getlist('photos')
		for photo in uploaded_photos:
			past_paper.photos.add(PastPaperPhoto.objects.create(file=photo))
		
		return HttpResponseRedirect(self.get_success_url())


class PastPaperDetail(DetailView):
	model = PastPaper
	context_object_name = 'past_paper'

	def get_context_data(self, **kwargs):
		NUM_LISTINGS = 5

		context = super().get_context_data(**kwargs)
		past_paper = self.object
		
		# similar_listings = PastPaper.objects.prefetch_related('photos').filter(
		# 	institution=listing.institution,
		# 	# listing.sub_category.name may throw an AttributeError if the listing has no sub_category (will be None.name)
		# 	sub_category__name__iexact=getattr(listing.sub_category, 'name', '')
		# ).only('title', 'price', 'datetime_added').order_by('-datetime_added')[0:NUM_LISTINGS]

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
		
		return context
