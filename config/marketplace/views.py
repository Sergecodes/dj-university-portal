import django_filters as filters
import os
from django_filters.views import FilterView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify
from django.utils.translation import get_language, gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from functools import reduce

from core.constants import (
	LISTING_PHOTOS_UPLOAD_DIR, AD_PHOTOS_UPLOAD_DIR,
	ITEM_LISTING_SUFFIX, AD_LISTING_SUFFIX,
	MIN_ITEM_PHOTOS_LENGTH  # todo enforce this !
)
from core.mixins import GetObjectMixin
from core.utils import get_photos
from flagging.models import Flag
from .forms import ItemListingForm, AdListingForm
from .mixins import CanDeleteListingMixin, CanEditListingMixin
from .models import (
	ItemListing, ItemCategory, 
	ItemListingPhoto, AdListing, AdListingPhoto
)

User = get_user_model()


# class ListingsExplain(TemplateView):
# 	template_name = 'marketplace/listings_explain.html'


class ItemListingCreate(LoginRequiredMixin, CreateView):
	form_class = ItemListingForm
	model = ItemListing
	template_name = 'marketplace/itemlisting_create.html'

	def get_form_kwargs(self, **kwargs):
		form_kwargs, request = super().get_form_kwargs(**kwargs), self.request
		user = request.user
		photos_list = request.session.get(user.username + ITEM_LISTING_SUFFIX, [])

		form_kwargs['user'] = user
		form_kwargs['initial_photos'] = get_photos(
			ItemListingPhoto, 
			photos_list, 
			LISTING_PHOTOS_UPLOAD_DIR
		)
		return form_kwargs

	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()

		# print(request.POST, request.FILES)
		# print(form.data)
		# print(form.data['sub_category'])
		# print(dir(form.fields['sub_category']))

		# update queryset of sub category field to ensure that sub category received is indeed a sub category of the passed category
		category_pk = request.POST.get('category', None)  
		category = get_object_or_404(ItemCategory, pk=category_pk)
		sub_category_field = form.fields['sub_category']
		sub_category_field.queryset = category.sub_categories.all()

		if form.is_valid():
			return self.form_valid(form)
		else:
			print(form.errors)
			return self.form_invalid(form)

	def form_valid(self, form):
		request = self.request
		session, username = request.session, request.user.username
		self.object = form.save(commit=False)
		listing = self.object
		listing.poster = request.user
		listing.original_language = get_language()
		listing.save()
		
		# add phone numbers to listing(phone_numbers is a queryset)
		phone_numbers = form.cleaned_data['contact_numbers']
		listing.contact_numbers.add(*[
			phone_number.id for phone_number in phone_numbers
		])

		# get list of photo names
		photos_list = session.get(username + ITEM_LISTING_SUFFIX)  

		# create photo instances pointing to the pre-created photos 
		# recall that these photos are already in the file system
		for photo_name in photos_list:
			photo = ItemListingPhoto()
			# path to file (relative path from MEDIA_ROOT)
			photo.file.name = os.path.join(LISTING_PHOTOS_UPLOAD_DIR, photo_name)
			# bulk=False saves the photo instance before adding
			# since photo already has file, no file will be created, just the model instance
			# note that this also implicitly does `photo.item_listing = listing`
			listing.photos.add(photo, bulk=False)  

		# remove photos list from session 
		request.session.pop(request.user.username + ITEM_LISTING_SUFFIX)

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return redirect(listing)


class ItemListingUpdate(GetObjectMixin, CanEditListingMixin, UpdateView):
	form_class = ItemListingForm
	model = ItemListing
	template_name = 'marketplace/itemlisting_update.html'

	def get_form_kwargs(self, **kwargs):
		form_kwargs = super().get_form_kwargs(**kwargs)
		listing, user, session = self.object, self.request.user, self.request.session

		# when form is initially displayed, get photos from listing
		# otherwise(after form invalid) get photos from session.
		if self.request.method == 'GET':
			listing_photos = listing.photos.all()
			# store photos in session
			photos_list = [photo.actual_filename for photo in listing_photos]
			session[user.username + ITEM_LISTING_SUFFIX] = photos_list
		else:
			photos_list = session.get(user.username + ITEM_LISTING_SUFFIX)
			listing_photos = get_photos(
				ItemListingPhoto, 
				photos_list, 
				LISTING_PHOTOS_UPLOAD_DIR
			)

		form_kwargs['user'] = user
		form_kwargs['initial_photos'] = listing_photos
		form_kwargs['update'] = True
		return form_kwargs

	def post(self, request, *args, **kwargs):
		# NOTE !! set self.object before making a form with self.get_form()
		# when overriding post method.
		self.object = self.get_object()
		form = self.get_form()
		
		# update queryset of sub category field to ensure that sub category received is indeed a sub category of the passed category
		category_pk = request.POST.get('category', None)  
		category = get_object_or_404(ItemCategory, pk=category_pk)
		sub_category_field = form.fields['sub_category']
		sub_category_field.queryset = category.sub_categories.all()
			
		# print(request.session.get(request.user.username + ITEM_LISTING_SUFFIX))
		if form.is_valid():
			return self.form_valid(form)
		else:
			print(form.errors)
			return self.form_invalid(form)

	def form_valid(self, form):
		request = self.request
		session, user = request.session, request.user

		# get object (form.instance) and update fields before saving.
		# this is better than calling form.save(commit=False);
		# with the latter, you have to set some m2m stuff... (see super method for details.)
		instance = form.instance	
		instance.poster = user
		instance.slug = slugify(instance.title)
		listing = form.save()
		
		## add phone numbers to listing(phone_numbers is a queryset)
		# first clear all listing's phone numbers
		listing.contact_numbers.clear()

		phone_numbers = form.cleaned_data['contact_numbers']
		listing.contact_numbers.add(*[
			phone_number.id for phone_number in phone_numbers
		])

		## reconstruct photos
		photos_list = session.get(user.username + ITEM_LISTING_SUFFIX)
		print(photos_list)
		# first clear all photos of instance
		listing.photos.clear()

		# create photo instances pointing to the pre-created photos 
		# recall that these photos are already in the file system
		for photo_name in photos_list:
			photo = ItemListingPhoto()
			# path to file (relative path from MEDIA_ROOT)
			photo.file.name = os.path.join(LISTING_PHOTOS_UPLOAD_DIR, photo_name)
			# bulk=False saves the photo instance before adding
			# since photo already has file, no file will be created, just the model instance
			# note that this also implicitly does `photo.item_listing = listing`
			listing.photos.add(photo, bulk=False)  

		# remove photos list from session 
		request.session.pop(user.username + ITEM_LISTING_SUFFIX)

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return redirect(listing)


class ItemListingDetail(DetailView):
	model = ItemListing
	context_object_name = 'listing'

	def get_context_data(self, **kwargs):
		NUM_LISTINGS = 5

		context = super().get_context_data(**kwargs)
		listing = self.object
		listing_photos = listing.photos.all()
		
		similar_listings = ItemListing.objects.prefetch_related('photos').filter(
			school=listing.school,
			# listing.sub_category.name may throw an AttributeError if the listing has no sub_category (will be None.name)
			sub_category__name=getattr(listing.sub_category, 'name', '')
		).only('title', 'price', 'posted_datetime')[:NUM_LISTINGS]
		
		# listing.sub_category.name may throw an AttributeError if the listing has no sub_category (will be None.name)
		sub_category_name = getattr(listing.sub_category, 'name', '')
		if sub_category_name:
			similar_listings = ItemListing.objects.prefetch_related('photos').filter(
				school=listing.school,
				sub_category__name=sub_category_name
			).only('title', 'price', 'posted_datetime')[:NUM_LISTINGS]
		else:
			similar_listings = ItemListing.objects.prefetch_related('photos').filter(
				school=listing.school
			).only('title', 'price', 'posted_datetime')[:NUM_LISTINGS]


		# get first photos of each similar listing
		first_photos = []
		for sim_listing in similar_listings:
			first_photos.append(sim_listing.photos.first())
		
		context['photos'] = listing_photos
		context['contact_numbers'] = listing.contact_numbers.all()
		context['bookmarkers'] = listing.bookmarkers.only('id')
		context['first_photos'] = first_photos
		context['similar_listings'] = similar_listings
		return context


class ItemListingDelete(GetObjectMixin, CanDeleteListingMixin, DeleteView):
	model = ItemListing
	success_url = reverse_lazy('marketplace:item-listing-list')


class ItemListingFilter(filters.FilterSet):
	title = filters.CharFilter(label=_('Item keywords'), method='filter_title')

	class Meta:
		model = ItemListing
		fields = ['school', 'title', 'category', ]

	def filter_title(self, queryset, name, value):
		print(value)
		value_list = value.split()
		print(value_list)

		qs = queryset.filter(
			reduce(lambda x, y: x | y, [Q(title__icontains=word) for word in value_list])
		)
		print(qs) 
		return qs

	# @property
	# def qs(self):
	# 	parent = super().qs
	# 	return parent.order_by('-posted_datetime')


class ItemListingList(FilterView):
	model = ItemListing
	# context_object_name = 'listings'
	filterset_class = ItemListingFilter
	template_name = 'marketplace/itemlisting_list.html'
	# change the suffix coz by default FilterView expects '_filter'
	template_name_suffix = '_list'
	paginate_by = 2
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		listings = self.object_list.prefetch_related('photos')
		
		# get first photos of each listing
		first_photos = []
		for listing in listings:
			first_photos.append(listing.photos.first())
		
		context['first_photos'] = first_photos
		return context


class AdListingCreate(LoginRequiredMixin, CreateView):
	form_class = AdListingForm
	model = AdListing
	template_name = 'marketplace/adlisting_create.html'

	def get_form_kwargs(self, **kwargs):
		form_kwargs, request = super().get_form_kwargs(**kwargs), self.request
		user = request.user
		photos_list = request.session.get(user.username + AD_LISTING_SUFFIX, [])

		form_kwargs['user'] = user
		form_kwargs['initial_photos'] = get_photos(
			AdListingPhoto, 
			photos_list, 
			AD_PHOTOS_UPLOAD_DIR
		)
		return form_kwargs

	def form_valid(self, form):
		request = self.request
		session, username = request.session, request.user.username
		self.object = form.save(commit=False)
		listing = self.object
		listing.poster = request.user
		listing.original_language = get_language()
		listing.save()
		
		# add phone numbers to listing(phone_numbers is a queryset)
		phone_numbers = form.cleaned_data['contact_numbers']
		listing.contact_numbers.add(*[
			phone_number.id for phone_number in phone_numbers
		])

		# create photo instances pointing to the pre-created photos.
		photos_list = session.get(username + AD_LISTING_SUFFIX, [])  # get list of photo names
		for photo_name in photos_list:
			photo = AdListingPhoto()
			# path to file (relative path from MEDIA_ROOT)
			photo.file.name = os.path.join(AD_PHOTOS_UPLOAD_DIR, photo_name)
			listing.photos.add(photo, bulk=False)  # bulk=False saves the photo instance before adding

		# remove photos list from session 
		# pop() default is empty list since adverts mustn't have photos
		request.session.pop(request.user.username + AD_LISTING_SUFFIX, [])

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return redirect(listing)


class AdListingUpdate(GetObjectMixin, CanEditListingMixin, UpdateView):
	form_class = AdListingForm
	model = AdListing
	template_name = 'marketplace/adlisting_update.html'

	def get_form_kwargs(self, **kwargs):
		form_kwargs = super().get_form_kwargs(**kwargs)
		listing, user, session = self.object, self.request.user, self.request.session

		# when form is initially displayed, get photos from listing
		# otherwise(after form invalid) get photos from session.
		if self.request.method == 'GET':
			listing_photos = listing.photos.all()
			# store photos in session
			photos_list = [photo.actual_filename for photo in listing_photos]

			# recall that photos are optional for adverts
			# so only update session if there are photos
			if photos_list:
				session[user.username + AD_LISTING_SUFFIX] = photos_list
		else:
			photos_list = session.get(user.username + AD_LISTING_SUFFIX, [])
			listing_photos = get_photos(
				AdListingPhoto, 
				photos_list, 
				AD_PHOTOS_UPLOAD_DIR
			)

		form_kwargs['user'] = user
		form_kwargs['initial_photos'] = listing_photos
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
		instance.slug = slugify(instance.title)
		listing = form.save()
		
		## add phone numbers to listing(phone_numbers is a queryset)
		# first clear all listing's phone numbers
		listing.contact_numbers.clear()

		phone_numbers = form.cleaned_data['contact_numbers']
		listing.contact_numbers.add(*[
			phone_number.id for phone_number in phone_numbers
		])

		## reconstruct photos
		photos_list = session.get(user.username + AD_LISTING_SUFFIX, [])

		# first clear all photos of instance
		listing.photos.clear()

		# create photo instances pointing to the pre-created photos 
		# recall that these photos are already in the file system
		for photo_name in photos_list:
			photo = AdListingPhoto()
			# path to file (relative path from MEDIA_ROOT)
			photo.file.name = os.path.join(AD_PHOTOS_UPLOAD_DIR, photo_name)
			# bulk=False saves the photo instance before adding
			# since photo already has file, no file will be created, just the model instance
			# note that this also implicitly does `photo.item_listing = listing`
			listing.photos.add(photo, bulk=False)  

		# remove photos list from session 
		request.session.pop(user.username + AD_LISTING_SUFFIX)

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return redirect(listing)


class AdListingDetail(DetailView):
	model = AdListing
	template_name = 'marketplace/adlisting_detail.html'
	context_object_name = 'listing'

	def get_context_data(self, **kwargs):
		NUM_LISTINGS = 5

		context = super().get_context_data(**kwargs)
		listing = self.object
		listing_photos = listing.photos.all()
		
		similar_listings = AdListing.objects.prefetch_related('photos').filter(
			school=listing.school,
			category__name=listing.category.name
		).only('title', 'pricing', 'posted_datetime')[0:NUM_LISTINGS]
		print(similar_listings)

		# get first photos of each similar listing
		first_photos = []
		# use a name other than 'listing' because of python's for loop scoping...
		for sim_listing in similar_listings:
			if sim_listing.photos.exists():
				first_photos.append(sim_listing.photos.first())
			else:
				first_photos.append(None)

		context['photos'] = listing_photos
		context['contact_numbers'] = listing.contact_numbers.all()
		context['bookmarkers'] = listing.bookmarkers.only('id')
		context['similar_listings'] = similar_listings
		context['first_photos'] = first_photos
		
		return context


class AdListingDelete(GetObjectMixin, CanDeleteListingMixin, DeleteView):
	model = AdListing
	success_url = reverse_lazy('marketplace:ad-listing-list')


class AdListingFilter(filters.FilterSet):
	title = filters.CharFilter(label=_('Advert keywords'), method='filter_title')

	class Meta:
		model = AdListing
		fields = ['school', 'title', 'category', ]

	def filter_title(self, queryset, name, value):
		value_list = value.split()
		qs = queryset.filter(
			reduce(lambda x, y: x | y, [Q(title__icontains=word) for word in value_list])
		)
		
		return qs


class AdListingList(FilterView):
	model = AdListing
	# context_object_name = 'listings'
	filterset_class = AdListingFilter
	template_name = 'marketplace/adlisting_list'
	template_name_suffix = '_list'
	paginate_by = 2
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		listings = self.object_list.prefetch_related('photos')
		
		# get first photos of each listing (for listings without photos, append `None`)
		first_photos = []
		for listing in listings:
			if listing.photos.exists():
				first_photos.append(listing.photos.first())
			else:
				first_photos.append(None)
		
		context['first_photos'] = first_photos
		return context
