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

    
