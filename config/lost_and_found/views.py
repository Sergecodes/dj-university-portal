import django_filters as filters
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import get_language, gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from .forms import FoundItemForm, LostItemForm
from .models import FoundItem, LostItem


class FoundItemCreate(LoginRequiredMixin, CreateView):
	form_class = FoundItemForm
	model = FoundItem
	template_name = 'lost_and_found/founditem_create.html'

	def get_form_kwargs(self, **kwargs):
		form_kwargs = super().get_form_kwargs(**kwargs)
		form_kwargs['user'] = self.request.user
		return form_kwargs

	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()

		if form.is_valid():
			return self.form_valid(form)
		else:
			print(form.errors)
			return self.form_invalid(form)

	def form_valid(self, form):
		request = self.request
		
		self.object = form.save(commit=False)
		found_item = self.object
		found_item.poster = request.user
		found_item.original_language = get_language()
		found_item.save()
		
		# add phone numbers (phone_numbers is a queryset)
		phone_numbers = form.cleaned_data['contact_numbers']
		for phone_number in phone_numbers:
			found_item.contact_numbers.add(phone_number)

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return HttpResponseRedirect(found_item.get_absolute_url())


class LostItemCreate(LoginRequiredMixin, CreateView):
	form_class = LostItemForm
	model = LostItem
	template_name = 'lost_and_found/lostitem_create.html'

	def get_form_kwargs(self, **kwargs):
		form_kwargs = super().get_form_kwargs(**kwargs)
		form_kwargs['user'] = self.request.user
		return form_kwargs

	def form_valid(self, form):
		request = self.request
		
		self.object = form.save(commit=False)
		lost_item = self.object
		lost_item.poster = request.user
		lost_item.original_language = get_language()
		lost_item.save()
		
		# add phone numbers (phone_numbers is a queryset)
		phone_numbers = form.cleaned_data['contact_numbers']
		for phone_number in phone_numbers:
			lost_item.contact_numbers.add(phone_number)

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return HttpResponseRedirect(lost_item.get_absolute_url())


class FoundItemList(ListView):
	model = FoundItem
	context_object_name = 'found_items'
	template_name='lost_and_found/founditem_list.html'


class LostItemList(ListView):
	model = LostItem
	context_object_name = 'lost_items'
	template_name='lost_and_found/lostitem_list.html'


class FoundItemDetail(DetailView):
	model = FoundItem
	context_object_name = 'found_item'


class LostItemDetail(DetailView):
	model = LostItem
	context_object_name = 'lost_item'

