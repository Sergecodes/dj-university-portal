import django_filters as filters
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from .forms import PastPaperForm, PastPaperPhotoForm
from .models import PastPaper, PastPaperPhoto


class PastPaperCreateView(CreateView):
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

		return self.get_success_url()

