import django_filters as filters
import os
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import get_language, gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from functools import reduce

from core.constants import LOST_ITEMS_PHOTOS_UPLOAD_DIR, LOST_ITEM_SUFFIX
from core.mixins import GetObjectMixin, IncrementViewCountMixin
from core.utils import get_photos, should_redirect
from .forms import FoundItemForm, LostItemForm
from .mixins import can_edit_item, can_delete_item, CanEditItemMixin, CanDeleteItemMixin
from .models import FoundItem, LostItem, LostItemPhoto


class FoundItemCreate(LoginRequiredMixin, CreateView):
	form_class = FoundItemForm
	model = FoundItem
	template_name = 'lost_and_found/founditem_create.html'

	def get_form_kwargs(self, **kwargs):
		form_kwargs = super().get_form_kwargs(**kwargs)
		form_kwargs['user'] = self.request.user
		return form_kwargs

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

		# Don't call the super() method here - you will end up saving the form twice. 
		# Instead handle the redirect yourself.
		return redirect(found_item)


class FoundItemDetail(GetObjectMixin, IncrementViewCountMixin, DetailView):
	model = FoundItem
	context_object_name = 'found_item'

	def get(self, request, *args, **kwargs):
		if should_redirect(object := self.get_object(), kwargs.get('slug')):
			return redirect(object, permanent=True)
		
		self.set_view_count()
		return super().get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user, item = self.request.user, self.object

		context['can_edit_item'] = can_edit_item(user, item)
		context['can_delete_item'] = can_delete_item(user, item)
		context['contact_numbers'] = self.object.contact_numbers.all()

		return context


class FoundItemFilter(filters.FilterSet):
	item_found = filters.CharFilter(label=_('Keywords'), method='filter_item')

	class Meta:
		model = FoundItem
		fields = ['school', 'item_found', ]

	def __init__(self, *args, **kwargs):
		# set label for fields,
		# this is so as to enable translation of labels.
		super().__init__(*args, **kwargs)
		# print(self.filters)
		self.filters['school'].label = _('School')

	def filter_item(self, queryset, name, value):
		value_list = value.split()
		qs = queryset.filter(
			reduce(
				lambda x, y: x | y, 
				[Q(item_found__icontains=word) for word in value_list]
			)
		)
		return qs


class FoundItemList(FilterView):
	model = FoundItem
	context_object_name = 'found_items'
	template_name = 'lost_and_found/founditem_list.html'
	filterset_class = FoundItemFilter
	template_name_suffix = '_list'
	paginate_by = 2


class FoundItemUpdate(GetObjectMixin, CanEditItemMixin, UpdateView):
	form_class = FoundItemForm
	model = FoundItem
	template_name = 'lost_and_found/founditem_update.html'

	def form_valid(self, form):
		found_item = form.save()
		
		## add phone numbers to found_item(phone_numbers is a queryset)
		# first clear all found_item's phone numbers
		found_item.contact_numbers.clear()

		phone_numbers = form.cleaned_data['contact_numbers']
		found_item.contact_numbers.add(*[
			phone_number.id for phone_number in phone_numbers
		])
		# Don't call the super() method here - you will end up saving the form twice. 
		# Instead handle the redirect yourself.
		return redirect(found_item)


class FoundItemDelete(GetObjectMixin, CanDeleteItemMixin, DeleteView):
	model = FoundItem
	success_url = reverse_lazy('lost_and_found:found-item-list')


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
		return redirect(lost_item)


class LostItemFilter(filters.FilterSet):
	item_lost = filters.CharFilter(label=_('Keywords'), method='filter_item')

	class Meta:
		model = LostItem
		fields = ['school', 'item_lost', ]

	def __init__(self, *args, **kwargs):
		# set label for fields,
		# this is so as to enable translation of labels.
		super().__init__(*args, **kwargs)
		self.filters['school'].label = _('School')

	def filter_item(self, queryset, name, value):
		value_list = value.split()
		qs = queryset.filter(
			reduce(
				lambda x, y: x | y, 
				[Q(item_lost__icontains=word) for word in value_list]
			)
		)
		return qs


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


class LostItemDetail(GetObjectMixin, IncrementViewCountMixin, DetailView):
	model = LostItem
	context_object_name = 'lost_item'

	def get(self, request, *args, **kwargs):
		if should_redirect(object := self.get_object(), kwargs.get('slug')):
			return redirect(object, permanent=True)
		
		self.set_view_count()
		return super().get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user, lost_item = self.request.user, self.object

		context['photos'] = lost_item.photos.all()
		context['can_edit_item'] = can_edit_item(user, lost_item)
		context['can_delete_item'] = can_delete_item(user, lost_item)
		context['contact_numbers'] = lost_item.contact_numbers.all()
		return context


class LostItemUpdate(GetObjectMixin, CanEditItemMixin, UpdateView):
	form_class = LostItemForm
	model = LostItem
	template_name = 'lost_and_found/lostitem_update.html'

	def get_form_kwargs(self, **kwargs):
		form_kwargs = super().get_form_kwargs(**kwargs)
		lost_item, user, session = self.object, self.request.user, self.request.session

		# when form is initially displayed, get photos from lost_item
		# otherwise(after form invalid) get photos from session.
		if self.request.method == 'GET':
			lost_item_photos = lost_item.photos.all()
			# store photos in session
			photos_list = [photo.actual_filename for photo in lost_item_photos]

			# recall that photos are optional for lost items
			# so only update session if there are photos
			if photos_list:
				session[user.username + LOST_ITEM_SUFFIX] = photos_list
		else:
			photos_list = session.get(user.username + LOST_ITEM_SUFFIX, [])
			lost_item_photos = get_photos(
				LostItemPhoto, 
				photos_list, 
				LOST_ITEMS_PHOTOS_UPLOAD_DIR
			)

		form_kwargs['user'] = user
		print(lost_item_photos)
		form_kwargs['initial_photos'] = lost_item_photos
		return form_kwargs

	def form_valid(self, form):
		request = self.request
		session, user = request.session, request.user
		lost_item = form.save()
		
		## add phone numbers to lost_item(phone_numbers is a queryset)
		# first clear all lost_item's phone numbers
		lost_item.contact_numbers.clear()

		phone_numbers = form.cleaned_data['contact_numbers']
		lost_item.contact_numbers.add(*[
			phone_number.id for phone_number in phone_numbers
		])

		## reconstruct photos
		photos_list = session.get(user.username + LOST_ITEM_SUFFIX, [])

		# first clear all photos of instance
		lost_item.photos.clear()

		# create photo instances pointing to the pre-created photos 
		# recall that these photos are already in the file system
		for photo_name in photos_list:
			photo = LostItemPhoto()
			# path to file (relative path from MEDIA_ROOT)
			photo.file.name = os.path.join(LOST_ITEMS_PHOTOS_UPLOAD_DIR, photo_name)
			# bulk=False saves the photo instance before adding
			# since photo already has file, no file will be created, just the model instance
			# note that this also implicitly does `photo.lost_item = lost_item`
			lost_item.photos.add(photo, bulk=False)  

		# remove photos list from session 
		request.session.pop(user.username + LOST_ITEM_SUFFIX)

		# Don't call the super() method here - you will end up saving the form twice. 
		# Instead handle the redirect yourself.
		return redirect(lost_item)


class LostItemDelete(GetObjectMixin, CanDeleteItemMixin, DeleteView):
	model = LostItem
	success_url = reverse_lazy('lost_and_found:lost-item-list')


