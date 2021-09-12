import django_filters as filters
import os
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

from core.constants import LOST_ITEMS_PHOTOS_UPLOAD_DIR, LOST_ITEM_SUFFIX
from core.utils import get_photos
from .forms import FoundItemForm, LostItemForm
from .models import FoundItem, LostItem, LostItemPhoto


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
		form_kwargs, request = super().get_form_kwargs(**kwargs), self.request
		user = request.user
		photos_list = request.session.get(user.username + LOST_ITEM_SUFFIX, [])

		form_kwargs['user'] = user
		form_kwargs['photos'] = get_photos(LostItemPhoto, photos_list, LOST_ITEMS_PHOTOS_UPLOAD_DIR)
		return form_kwargs

	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()

		if form.is_valid():
			return self.form_valid(form)
		else:
			# remove and return photos list from session (note that the uploaded photos will be lost by default)
			# photos_list = request.session.pop(request.user.username+LOST_ITEM_SUFFIX, [])

			# delete uploaded photos(and also remove corresponding files)
			# no need to delete photos. this will cause unneccessary load on server. instead, just allow the photos, but regularly remove photos not linked to model instances.
			# for photo_name in photos_list:
			# 	# todo code to delete file here..
			# 	pass

			print(form.errors)
			return self.form_invalid(form)	

	def form_valid(self, form):
		request = self.request
		user = request.user
		session, username = request.session, user.username
		
		self.object = form.save(commit=False)
		lost_item = self.object
		lost_item.poster = user
		lost_item.original_language = get_language()
		lost_item.save()
		
		# add phone numbers (phone_numbers is a queryset)
		phone_numbers = form.cleaned_data['contact_numbers']
		for phone_number in phone_numbers:
			lost_item.contact_numbers.add(phone_number)

		# create photo instances pointing to the pre-created photos.
		photos_list = session.get(username + LOST_ITEM_SUFFIX, [])  # get list of photo names
		print(photos_list)

		for photo_name in photos_list:
			photo = LostItemPhoto()
			# path to file (relative path from MEDIA_ROOT)
			photo.file.name = os.path.join(LOST_ITEMS_PHOTOS_UPLOAD_DIR, photo_name)
			lost_item.photos.add(photo, bulk=False)  # bulk=False saves the photo instance before adding

		# remove photos list from session 
		# pop() default is empty list since photos are optional
		request.session.pop(user.username + LOST_ITEM_SUFFIX, [])

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return HttpResponseRedirect(lost_item.get_absolute_url())


class FoundItemFilter(filters.FilterSet):
	item_found = filters.CharFilter(label=_('Keyword'), lookup_expr='icontains')

	class Meta:
		model = FoundItem
		fields = ['school', 'item_found', ]

	@property
	def qs(self):
		parent = super().qs
		return parent.order_by('-posted_datetime')


class FoundItemList(FilterView):
	model = FoundItem
	context_object_name = 'found_items'
	template_name = 'lost_and_found/founditem_list.html'
	filterset_class = FoundItemFilter
	template_name_suffix = '_list'
	paginate_by = 2

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		# found_items = self.object_list
		
		return context


class LostItemFilter(filters.FilterSet):
	item_lost = filters.CharFilter(label=_('Keyword'), lookup_expr='icontains')

	class Meta:
		model = LostItem
		fields = ['school', 'item_lost', ]

	@property
	def qs(self):
		parent = super().qs
		return parent.order_by('-posted_datetime')


class LostItemList(FilterView):
	model = LostItem
	context_object_name = 'lost_items'
	template_name = 'lost_and_found/lostitem_list.html'
	filterset_class = LostItemFilter
	template_name_suffix = '_list'
	paginate_by = 2

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		lost_items = self.object_list
		
		# get first photos of each lost_item (for lost_items without photos, append `None`)
		first_photos = []
		for lost_item in lost_items:
			if lost_item.photos.exists():
				first_photos.append(lost_item.photos.first())
			else:
				first_photos.append(None)
		
		context['first_photos'] = first_photos
		return context


class FoundItemDetail(DetailView):
	model = FoundItem
	context_object_name = 'found_item'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['contact_numbers'] = self.object.contact_numbers.all()

		return context


class LostItemDetail(DetailView):
	model = LostItem
	context_object_name = 'lost_item'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		lost_item = self.object

		context['photos'] = lost_item.photos.all()
		context['contact_numbers'] = lost_item.contact_numbers.all()
		# context['is_mobile'] = lost_item.

		return context

