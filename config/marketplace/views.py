import django_filters as filters
import os
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import get_language, ugettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from core.constants import (
	LISTING_PHOTOS_UPLOAD_DIR, 
	AD_PHOTOS_UPLOAD_DIR,
	MIN_LISTING_PHOTOS_LENGTH  # todo enforce this !
)
from .forms import ItemListingForm, AdListingForm
from .models import (
	ItemListing, ItemCategory, 
	ItemListingPhoto, AdListing, AdListingPhoto
)


class ItemListingCreate(LoginRequiredMixin, CreateView):
	form_class = ItemListingForm
	model = ItemListing
	template_name = 'marketplace/itemlisting_create.html'
	# success_url = reverse_lazy('marketplace:item-listing-list')

	def get_form_kwargs(self, **kwargs):
		form_kwargs = super().get_form_kwargs(**kwargs)
		form_kwargs['user'] = self.request.user
		return form_kwargs

	def get(self, request, *args, **kwargs):
		# remove photos list from session (just in case... e.g if user previously started filling form but didn't finish..)
		request.session.pop(request.user.username, [])
		
		return super().get(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()

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
			# remove and return photos list from session (note that the uploaded photos will be lost by default)
			photos_list = request.session.pop(request.user.username, [])

			# delete uploaded photos(and also remove corresponding files)
			# no need to delete photos. this will cause unneccessary load on server. instead, just allow the photos, but regularly remove photos not linked to model instances.
			# for photo_name in photos_list:
			# 	# todo code to delete file here..
			# 	pass

			print(form.errors)
			return self.form_invalid(form)

	def form_valid(self, form):
		request = self.request
		session, username = request.session, request.user.username
		self.object = form.save(commit=False)
		listing = self.object
		listing.owner = request.user
		listing.save()
		
		# add phone numbers (phone_numbers is a queryset)
		phone_numbers = form.cleaned_data['contact_numbers']

		# this loop isn't a case for concern since the phone numbers will generally be at most 5 right?
		print(phone_numbers)  
		for phone_number in phone_numbers:
			listing.contact_numbers.add(phone_number)

		# create photo instances pointing to the pre-created photos.
		photos_list = session.get(username, [])  # get list of photo names
		print(photos_list)

		for photo_name in photos_list:
			photo = ItemListingPhoto()
			# path to file (relative path from MEDIA_ROOT)
			photo.file.name = os.path.join(LISTING_PHOTOS_UPLOAD_DIR, photo_name)
			listing.photos.add(photo, bulk=False)  # bulk=False saves the photo instance before adding

		# remove photos list from session 
		request.session.pop(request.user.username)

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return HttpResponseRedirect(listing.get_absolute_url())


class AdListingCreate(LoginRequiredMixin, CreateView):
	form_class = AdListingForm
	model = AdListing
	template_name = 'marketplace/adlisting_create.html'
	success_url = reverse_lazy('marketplace:ad-listing-list')

	def get_form_kwargs(self, **kwargs):
		form_kwargs = super().get_form_kwargs(**kwargs)
		form_kwargs['user'] = self.request.user
		return form_kwargs

	def get(self, request, *args, **kwargs):
		# remove photos list from session (just in case...)
		request.session.pop(request.user.username, [])
		return super().get(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()

		if form.is_valid():
			return self.form_valid(form)
		else:
			# remove and return photos list from session 
			photos_list = request.session.pop(request.user.username, [])

			# delete uploaded photos(and also remove corresponding files)
			# no need to delete photos. this will cause unneccessary load on server. instead, just allow the photos, but regularly remove photos not linked to model instances.
			# for photo_name in photos_list:
			# 	# todo code to delete file here..
			# 	pass

			print(form.errors)
			return self.form_invalid(form)

	def form_valid(self, form):
		request = self.request
		session, username = request.session, request.user.username
		self.object = form.save(commit=False)
		listing = self.object
		listing.owner = request.user
		listing.save()
		
		# add phone numbers
		phone_numbers = form.cleaned_data['contact_numbers']
		for phone_number in phone_numbers:
			listing.contact_numbers.add(phone_number)

		# create photo instances pointing to the pre-created photos.
		photos_list = session.get(username, [])  # get list of photo names
		for photo_name in photos_list:
			photo = AdListingPhoto()
			# path to file (relative path from MEDIA_ROOT)
			photo.file.name = os.path.join(AD_PHOTOS_UPLOAD_DIR, photo_name)
			listing.photos.add(photo, bulk=False)  # bulk=False saves the photo instance before adding

		# remove photos list from session 
		request.session.pop(request.user.username, [])

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return HttpResponseRedirect(self.get_success_url())


class ItemListingDetail(DetailView):
	model = ItemListing
	context_object_name = 'listing'

	def get_context_data(self, **kwargs):
		NUM_LISTINGS = 5

		context = super().get_context_data(**kwargs)
		listing = self.object
		listing_photos = listing.photos.all()
		
		similar_listings = ItemListing.objects.prefetch_related('photos').filter(
			institution=listing.institution,
			# listing.sub_category.name may throw an AttributeError if the listing has no sub_category (will be None.name)
			sub_category__name=getattr(listing.sub_category, 'name', '')
		).only('title', 'price', 'datetime_added').order_by('-datetime_added')[0:NUM_LISTINGS]
		
		# listing.sub_category.name may throw an AttributeError if the listing has no sub_category (will be None.name)
		sub_category_name = getattr(listing.sub_category, 'name', '')
		if sub_category_name:
			similar_listings = ItemListing.objects.prefetch_related('photos').filter(
				institution=listing.institution,
				sub_category__name=sub_category_name
			).only('title', 'price', 'datetime_added').order_by('-datetime_added')[0:NUM_LISTINGS]
		else:
			similar_listings = ItemListing.objects.prefetch_related('photos').filter(
				institution=listing.institution
			).only('title', 'price', 'datetime_added').order_by('-datetime_added')[0:NUM_LISTINGS]


		# get first photos of each similar listing
		first_photos = []
		for sim_listing in similar_listings:
			first_photos.append(sim_listing.photos.first())
		
		context['photos'] = listing_photos
		context['contact_numbers'] = listing.contact_numbers.all()
		context['first_photos'] = first_photos
		context['similar_listings'] = similar_listings
		return context


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
			institution=listing.institution,
			category__name=listing.category.name
		).only('title', 'pricing', 'datetime_added').order_by('-datetime_added')[0:NUM_LISTINGS]
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
		context['similar_listings'] = similar_listings
		context['first_photos'] = first_photos
		
		return context


class ItemListingFilter(filters.FilterSet):
	title = filters.CharFilter(label=_('Item keyword'), lookup_expr='icontains')

	class Meta:
		model = ItemListing
		fields = ['institution', 'title', 'category', ]

	@property
	def qs(self):
		parent = super().qs
		return parent.order_by('-datetime_added')


class ItemListingList(FilterView):
	model = ItemListing
	# context_object_name = 'listings'
	filterset_class = ItemListingFilter
	template_name = 'marketplace/itemlisting_list.html'
	# change the suffix coz by default filterview expects '_filter'
	template_name_suffix = '_list'
	paginate_by = 2
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		listings = self.object_list
		
		# get first photos of each listing
		first_photos = []
		for listing in listings:
			first_photos.append(listing.photos.first())
		
		context['first_photos'] = first_photos
		return context


class AdListingFilter(filters.FilterSet):
	title = filters.CharFilter(label=_('Advert keyword'), lookup_expr='icontains')

	class Meta:
		model = AdListing
		fields = ['institution', 'title', 'category', ]

	@property
	def qs(self):
		parent = super().qs
		return parent.order_by('-datetime_added')


class AdListingList(FilterView):
	model = AdListing
	# context_object_name = 'listings'
	filterset_class = AdListingFilter
	template_name = 'marketplace/adlisting_list'
	template_name_suffix = '_list'
	paginate_by = 2
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		listings = self.object_list
		
		# get first photos of each listing (for listings without photos, append `None`)
		first_photos = []
		for listing in listings:
			if listing.photos.exists():
				first_photos.append(listing.photos.first())
			else:
				first_photos.append(None)
		
		context['first_photos'] = first_photos
		return context
