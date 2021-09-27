import django_filters as filters
import os
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import get_language, gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from core.constants import REQUESTED_ITEMS_PHOTOS_UPLOAD_DIR, REQUESTED_ITEM_SUFFIX
from core.utils import get_photos
from .forms import RequestedItemForm
from .models import RequestedItem, RequestedItemPhoto


class RequestedItemCreate(LoginRequiredMixin, CreateView):
	form_class = RequestedItemForm
	model = RequestedItem
	template_name = 'requested_items/requested_item_create.html'

	def get_form_kwargs(self, **kwargs):
		form_kwargs, request = super().get_form_kwargs(**kwargs), self.request
		user = request.user
		photos_list = request.session.get(user.username + REQUESTED_ITEM_SUFFIX, [])

		form_kwargs['user'] = user
		form_kwargs['photos'] = get_photos(RequestedItemPhoto, photos_list, REQUESTED_ITEMS_PHOTOS_UPLOAD_DIR)
		return form_kwargs

	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()

		if form.is_valid():
			return self.form_valid(form)
		else:
			# remove and return photos list from session (note that the uploaded photos will be lost by default)
			# photos_list = request.session.pop(request.user.username+REQUESTED_ITEM_SUFFIX, [])

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
		requested_item = self.object
		requested_item.poster = user
		requested_item.original_language = get_language()
		requested_item.save()
		
		# add phone numbers (phone_numbers is a queryset)
		phone_numbers = form.cleaned_data['contact_numbers']
		for phone_number in phone_numbers:
			requested_item.contact_numbers.add(phone_number)

		# create photo instances pointing to the pre-created photos.
		photos_list = session.get(username + REQUESTED_ITEM_SUFFIX, [])  # get list of photo names
		print(photos_list)

		for photo_name in photos_list:
			photo = RequestedItemPhoto()
			# path to file (relative path from MEDIA_ROOT)
			photo.file.name = os.path.join(REQUESTED_ITEMS_PHOTOS_UPLOAD_DIR, photo_name)
			requested_item.photos.add(photo, bulk=False)  # bulk=False saves the photo instance before adding

		# remove photos list from session 
		# pop() default is empty list since photos are optional
		request.session.pop(user.username + REQUESTED_ITEM_SUFFIX, [])

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return HttpResponseRedirect(requested_item.get_absolute_url())


class RequestedItemFilter(filters.FilterSet):
	item_requested = filters.CharFilter(label=_('Keyword'), lookup_expr='icontains')

	class Meta:
		model = RequestedItem
		fields = ['school', 'item_requested', ]

	@property
	def qs(self):
		parent = super().qs
		return parent.order_by('-posted_datetime')


class RequestedItemList(FilterView):
	model = RequestedItem
	context_object_name = 'lost_items'
	template_name = 'requested_items/requested_item_list.html'
	filterset_class = RequestedItemFilter
	template_name_suffix = '_list'
	paginate_by = 2

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		requested_items = self.object_list
		
		# get first photos of each lost_item (for requested_items without photos, append `None`)
		first_photos = []
		for requested_item in requested_items:
			if requested_item.photos.exists():
				first_photos.append(requested_item.photos.first())
			else:
				first_photos.append(None)
		
		context['first_photos'] = first_photos
		return context


class RequestedItemDetail(DetailView):
	model = RequestedItem
	template_name = 'requested_items/requested_item_detail.html'
	context_object_name = 'requested_item'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		requested_item = self.object

		context['photos'] = requested_item.photos.all()
		context['contact_numbers'] = requested_item.contact_numbers.all()

		return context

