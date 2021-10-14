import django_filters as filters
import os
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.translation import get_language, gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from functools import reduce

from core.constants import REQUESTED_ITEMS_PHOTOS_UPLOAD_DIR, REQUESTED_ITEM_SUFFIX
from core.mixins import GetObjectMixin, IncrementViewCountMixin
from core.utils import get_photos, should_redirect
from .forms import RequestedItemForm
from .mixins import (
	can_edit_item, can_delete_item,
	CanDeleteRequestedItemMixin, CanEditRequestedItemMixin
)
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
		form_kwargs['initial_photos'] = get_photos(photos_list, REQUESTED_ITEMS_PHOTOS_UPLOAD_DIR)
		return form_kwargs

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
		return redirect(requested_item)


class RequestedItemUpdate(GetObjectMixin, CanEditRequestedItemMixin, UpdateView):
	form_class = RequestedItemForm
	model = RequestedItem
	template_name = 'requested_items/requested_item_update.html'

	def get_form_kwargs(self, **kwargs):
		form_kwargs = super().get_form_kwargs(**kwargs)
		item, user, session = self.object, self.request.user, self.request.session

		# when form is initially displayed, get photos from item
		# otherwise(after form invalid) get photos from session.
		if self.request.method == 'GET':
			item_photos = item.photos.all()
			# store photos in session
			photos_list = [photo.actual_filename for photo in item_photos]

			# recall that photos are optional for adverts
			# so only update session if there are photos
			if photos_list:
				session[user.username + REQUESTED_ITEM_SUFFIX] = photos_list
		else:
			photos_list = session.get(user.username + REQUESTED_ITEM_SUFFIX, [])
			item_photos = get_photos( photos_list, REQUESTED_ITEMS_PHOTOS_UPLOAD_DIR)

		form_kwargs['user'] = user
		form_kwargs['initial_photos'] = item_photos
		form_kwargs['update'] = True
		return form_kwargs

	def form_valid(self, form):
		request = self.request
		session, user = request.session, request.user

		# get object (form.instance) and update fields before saving.
		# this is better than calling form.save(commit=False);
		# with the latter, you have to set some m2m stuff... (see super method for details.)
		instance = form.instance	
		instance.poster = user
		instance.slug = slugify(instance.item_requested)
		requested_item = form.save()
		
		## add phone numbers to requested_item(phone_numbers is a queryset)
		# first clear all requested_item's phone numbers
		requested_item.contact_numbers.clear()

		phone_numbers = form.cleaned_data['contact_numbers']
		requested_item.contact_numbers.add(*[
			phone_number.id for phone_number in phone_numbers
		])

		## Reconstruct photos
		photos_list = session.get(user.username + REQUESTED_ITEM_SUFFIX, [])

		# first clear all photos of instance
		requested_item.photos.clear()

		# create photo instances pointing to the pre-created photos 
		# recall that these photos are already in the file system
		for photo_name in photos_list:
			photo = RequestedItemPhoto()
			# path to file (relative path from MEDIA_ROOT)
			photo.file.name = os.path.join(REQUESTED_ITEMS_PHOTOS_UPLOAD_DIR, photo_name)
			# bulk=False saves the photo instance before adding
			# since photo already has file, no file will be created, just the model instance
			# note that this also implicitly does `photo.requested_item = requested_item`
			requested_item.photos.add(photo, bulk=False)  

		# remove photos list from session 
		request.session.pop(user.username + REQUESTED_ITEM_SUFFIX)

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return redirect(requested_item)


class RequestedItemDelete(GetObjectMixin, CanDeleteRequestedItemMixin, DeleteView):
	model = RequestedItem
	success_url = reverse_lazy('requested_items:requested-item-list')


class RequestedItemFilter(filters.FilterSet):
	item_requested = filters.CharFilter(label=_('Keywords'), method='filter_item')

	class Meta:
		model = RequestedItem
		fields = ['school', 'item_requested', 'category', ]
	
	def __init__(self, *args, **kwargs):
		# set label for fields,
		# this is to enable translation of labels.
		super().__init__(*args, **kwargs)
		self.filters['school'].label = _('School')
		self.filters['category'].label = _('Category')

	def filter_item(self, queryset, name, value):
		value_list = value.split()
		qs = queryset.filter(
			reduce(
				lambda x, y: x | y, 
				[Q(item_requested__icontains=word) for word in value_list]
			)
		)
		
		return qs


class RequestedItemList(FilterView):
	model = RequestedItem
	context_object_name = 'requested_items'
	template_name = 'requested_items/requested_item_list.html'
	filterset_class = RequestedItemFilter
	template_name_suffix = '_list'
	paginate_by = 2

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		requested_items = self.object_list
		
		# get first photos of each requested_item (for requested_items without photos, append `None`)
		first_photos = []
		for requested_item in requested_items:
			if requested_item.photos.exists():
				first_photos.append(requested_item.photos.first())
			else:
				first_photos.append(None)
		
		context['first_photos'] = first_photos
		return context


class RequestedItemDetail(GetObjectMixin, IncrementViewCountMixin, DetailView):
	model = RequestedItem
	template_name = 'requested_items/requested_item_detail.html'
	context_object_name = 'requested_item'

	def get(self, request, *args, **kwargs):
		if should_redirect(object := self.get_object(), kwargs.get('slug')):
			return redirect(object, permanent=True)
		
		self.set_view_count()
		return super().get(request, *args, **kwargs)
		
	def get_context_data(self, **kwargs):
		NUM_ITEMS = 4
		user = self.request.user
		context = super().get_context_data(**kwargs)
		requested_item = self.object

		## similar items
		similar_items = RequestedItem.objects.prefetch_related('photos').filter(
			school=requested_item.school,
			category__name=requested_item.category.name
		).exclude(id=requested_item.id) \
		.only('item_requested', 'price_at_hand', 'posted_datetime')[:NUM_ITEMS]

		# get first photos of each similar item
		first_photos = []
		# use a name other than 'item' because of python's for loop scoping...
		for item in similar_items:
			if item.photos.exists():
				first_photos.append(item.photos.first())
			else:
				first_photos.append(None)

		context['photos'] = requested_item.photos.all()
		context['contact_numbers'] = requested_item.contact_numbers.all()
		context['similar_items'] = similar_items
		context['first_photos'] = first_photos
		context['can_edit_item'] = False if user.is_anonymous else can_edit_item(user, requested_item)
		context['can_delete_item'] = False if user.is_anonymous else can_delete_item(user, requested_item)

		return context


## Bookmarking
@login_required
@require_POST
def requested_item_bookmark_toggle(request):
	"""This view handles bookmarking for past papers"""
	user, POST = request.user, request.POST
	id, action = POST.get('id'), POST.get('action')
	requested_item = get_object_or_404(RequestedItem, pk=id)

	# if vote is new (not removing bookmark)
	if action == 'bookmark':
		requested_item.bookmarkers.add(user)
		return JsonResponse({'bookmarked': True}, status=200)

	# if user is retracting bookmark
	elif action == 'recall-bookmark':
		requested_item.bookmarkers.remove(user)
		return JsonResponse({'unbookmarked': True}, status=200)
	else:
		return JsonResponse({'error': _('Invalid action')}, status=400)

