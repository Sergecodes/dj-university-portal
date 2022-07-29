import django_filters as filters
import os
from django_filters.views import FilterView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.translation import get_language, gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from functools import reduce

from core.constants import (
	LISTING_PHOTOS_UPLOAD_DIR, AD_PHOTOS_UPLOAD_DIR,
	ITEM_LISTING_SUFFIX, AD_LISTING_SUFFIX,
	MIN_ITEM_PHOTOS_LENGTH, 
)
from core.mixins import GetObjectMixin, IncrementViewCountMixin
from core.models import Country
from core.utils import get_photos, should_redirect, translate_text
from ..forms import ItemListingForm, AdListingForm
from ..mixins import (
	can_edit_listing, can_delete_listing, 
	CanDeleteListingMixin, CanEditListingMixin
)
from ..models import (
	ItemListing, ItemCategory, 
	ItemListingPhoto, AdListing, AdListingPhoto
)

User = get_user_model()


class ItemListingCreate(LoginRequiredMixin, CreateView):
	form_class = ItemListingForm
	model = ItemListing
	template_name = 'marketplace/itemlisting_create.html'

	def get_form_kwargs(self, **kwargs):
		form_kwargs, request = super().get_form_kwargs(**kwargs), self.request
		user = request.user
		photos_list = request.session.get(user.username + ITEM_LISTING_SUFFIX, [])

		form_kwargs['user'] = user
		form_kwargs['country_or_code'] = request.session.get('country_code', user.country)
		form_kwargs['initial_photos'] = get_photos(photos_list, LISTING_PHOTOS_UPLOAD_DIR)
		return form_kwargs

	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		session, username = request.session, request.user.username

		# Validate minimum number of photos (backend)
		# this check is also done on the frontend; but in an almost naive way..
		# - counting the number of html photo containers.
		# no need to validate max number since the photo upload ajax view already does that
		num_photos = len(session.get(username + ITEM_LISTING_SUFFIX, []))
		if num_photos < MIN_ITEM_PHOTOS_LENGTH:
			form.add_error(
				None, 
				_('Upload at least {} photos.'.format(MIN_ITEM_PHOTOS_LENGTH))
			)

		## Validate that sub category belongs to category and that city belongs to country
		# update queryset of sub category field to ensure that sub category received 
		# is indeed a sub category of the passed category
		category_pk = request.POST.get('category')  
		category = get_object_or_404(ItemCategory, pk=category_pk)
		sub_category_field = form.fields['sub_category']
		sub_category_field.queryset = category.sub_categories.all()

		country_pk = request.POST.get('country')
		country = get_object_or_404(Country, pk=country_pk)
		city_field = form.fields['city']
		city_field.queryset = country.cities.all()

		if form.is_valid():
			return self.form_valid(form)
		else:
			# print(form.errors)
			return self.form_invalid(form)

	def form_valid(self, form):
		session, user = self.request.session, self.request.user
		self.object = form.save(commit=False)
		listing = self.object
		current_lang = get_language()

		## TRANSLATION
		if settings.ENABLE_GOOGLE_TRANSLATE:
			# get language to translate to
			trans_lang = 'fr' if current_lang == 'en' else 'en'

			translatable_fields = ['title', 'description', 'condition_description', ]
			translate_fields = [field + '_' + trans_lang for field in translatable_fields]
			
			# fields that need to be translated. (see translation.py)
			# ommit slug because google corrects the slug to appropriate string b4 translating.
			# see demo in google translate .
			field_values = [getattr(listing, field) for field in translatable_fields]
			trans_results = translate_text(field_values, trans_lang)
			
			# each dict in trans_results contains keys: 
			# `input`, `translatedText`, `detectedSourceLanguage`
			for trans_field, result_dict in zip(translate_fields, trans_results):
				setattr(listing, trans_field, result_dict['translatedText'])

			# if object was saved in say english, slug_en will be set but not slug_fr. 
			# so get the slug in the other language
			# also, at this point, these attributes will be set(translated)
			if trans_lang == 'fr':
				listing.slug_fr = slugify(listing.title_fr)
			elif trans_lang == 'en':
				listing.slug_en = slugify(listing.title_en)

		with transaction.atomic():
			listing.poster = user
			listing.original_language = current_lang
			listing.save()
			
			# add phone numbers to listing(phone_numbers is a queryset)
			listing.contact_numbers.add(*form.cleaned_data['contact_numbers'])

			# get list of photo names
			photos_list = session.get(user.username + ITEM_LISTING_SUFFIX)  

			# create photo instances pointing to the pre-created photos 
			# recall that these photos are already in the file system
			listing_photos = []
			for photo_name in photos_list:
				photo = ItemListingPhoto()
				# path to file (relative path from MEDIA_ROOT)
				photo.file.name = os.path.join(LISTING_PHOTOS_UPLOAD_DIR, photo_name)
				listing_photos.append(photo)

			# bulk=False saves the photo instance before adding
			# since photo already has file, no file will be created, just the model instance
			# note that this also implicitly does `photo.item_listing = listing`
			# see https://docs.djangoproject.com/en/3.2/ref/models/relations/#django.db.models.fields.related.RelatedManager.add
			listing.photos.add(*listing_photos, bulk=False)

		# remove photos list from session 
		session.pop(user.username + ITEM_LISTING_SUFFIX)

		# Don't call the super() method here - you will end up saving the form twice.
		# Instead handle the redirect yourself.
		return redirect(listing)


class ItemListingUpdate(GetObjectMixin, CanEditListingMixin, UpdateView):
	form_class = ItemListingForm
	model = ItemListing
	template_name = 'marketplace/itemlisting_update.html'

	def get_form_kwargs(self, **kwargs):
		form_kwargs, request = super().get_form_kwargs(**kwargs), self.request
		listing, user, session = self.object, request.user, request.session

		# when form is initially displayed, get photos from listing
		# otherwise(after form invalid) get photos from session.
		if request.method == 'GET':
			# store photos in session
			photos_list = [photo.actual_filename for photo in listing.photos.all()]
			session[user.username + ITEM_LISTING_SUFFIX] = photos_list
		else:
			photos_list = session.get(user.username + ITEM_LISTING_SUFFIX)

		form_kwargs['user'] = user
		form_kwargs['country_or_code'] = request.session.get('country_code', user.country)
		form_kwargs['initial_photos'] = get_photos(photos_list, LISTING_PHOTOS_UPLOAD_DIR)
		form_kwargs['update'] = True
		return form_kwargs

	def post(self, request, *args, **kwargs):
		# NOTE !! ALWAYS set self.object before making a form with self.get_form()
		# when overriding post method.
		self.object = self.get_object()
		form = self.get_form()
		session, username = request.session, request.user.username

		# validate minimum number of photos 
		# no need to validate max number since the photo upload ajax view already does that
		num_photos = len(session.get(username + ITEM_LISTING_SUFFIX, []))
		if num_photos < MIN_ITEM_PHOTOS_LENGTH:
			form.add_error(
				None, 
				_('Upload at least {} photos.'.format(MIN_ITEM_PHOTOS_LENGTH))
			)
		
		## Validate that sub category belongs to category and that city belongs to country
		category_pk = request.POST.get('category')  
		category = get_object_or_404(ItemCategory, pk=category_pk)
		sub_category_field = form.fields['sub_category']
		sub_category_field.queryset = category.sub_categories.all()

		country_pk = request.POST.get('country')
		country = get_object_or_404(Country, pk=country_pk)
		city_field = form.fields['city']
		city_field.queryset = country.cities.all()
			
		if form.is_valid():
			return self.form_valid(form)
		else:
			# print(form.errors)
			return self.form_invalid(form)

	def form_valid(self, form):
		session, user = self.request.session, self.request.user
		listing = form.save(commit=False)
		current_lang = get_language()

		## TRANSLATION
		if settings.ENABLE_GOOGLE_TRANSLATE:
			changed_data = form.changed_data

			# get fields that are translatable(permitted to be translated)
			permitted_fields = ['title', 'description', 'condition_description', ]

			updated_fields = [
				field for field in changed_data if \
				not field.endswith('_en') and not field.endswith('_fr')
			]
			desired_fields = [field for field in updated_fields if field in permitted_fields]

			trans_lang = 'fr' if current_lang == 'en' else 'en'

			# get and translated values that need to be translated
			field_values = [getattr(listing, field) for field in desired_fields]

			if field_values:
				trans_results = translate_text(field_values, trans_lang)
				
				# get fields that need to be set after translation
				translate_fields = [field + '_' + trans_lang for field in desired_fields]

				# each dict in trans_results contains keys: 
				# `input`, `translatedText`, `detectedSourceLanguage`
				for trans_field, result_dict in zip(translate_fields, trans_results):
					setattr(listing, trans_field, result_dict['translatedText'])

		with transaction.atomic():
			listing.update_language = current_lang
			listing.save()
			
			# Add phone numbers to listing(phone_numbers is a queryset)
			listing.contact_numbers.set(form.cleaned_data['contact_numbers'], clear=True)

			# Update photos
			photos_list = session.get(user.username + ITEM_LISTING_SUFFIX)
			listing_photos = []
			for photo_name in photos_list:
				photo = ItemListingPhoto()
				# path to file (relative path from MEDIA_ROOT)
				photo.file.name = os.path.join(LISTING_PHOTOS_UPLOAD_DIR, photo_name)
				listing_photos.append(photo)

			# see https://docs.djangoproject.com/en/3.2/ref/models/relations/#django.db.models.fields.related.RelatedManager.set
			listing.photos.set(listing_photos, bulk=False, clear=True)

		# remove photos list from session 
		session.pop(user.username + ITEM_LISTING_SUFFIX)

		# Don't call the super() method here - you will end up saving the form twice. 
		# Instead handle the redirect yourself.
		return redirect(listing)


class ItemListingDetail(GetObjectMixin, IncrementViewCountMixin, DetailView):
	model = ItemListing
	context_object_name = 'listing'

	def get(self, request, *args, **kwargs):
		if should_redirect(object := self.get_object(), kwargs.get('slug')):
			return redirect(object, permanent=True)
		
		self.set_view_count()
		return super().get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		NUM_LISTINGS = 5
		user, listing = self.request.user, self.object
		context = super().get_context_data(**kwargs)
		
		# Accesing the listing's city or country won't hit the database
		#
		# Exclude current object from list of similar objects and slice queryset
		# note that we can't filter queryset after slice has been taken
		similar_listings = ItemListing.objects \
			.select_related('city__country') \
			.prefetch_related('photos') \
			.filter(city=listing.city, sub_category=listing.sub_category) \
			.exclude(id=listing.id) \
			.only('city', 'title', 'price', 'posted_datetime')[:NUM_LISTINGS]

		# get first photos of each similar listing
		first_photos = []
		for sim_listing in similar_listings:
			first_photos.append(sim_listing.photos.first())
		
		context['photos'] = listing.photos.all()
		context['contact_numbers'] = listing.contact_numbers.all()
		context['bookmarkers'] = listing.bookmarkers.only('id')
		context['first_photos'] = first_photos
		context['similar_listings'] = similar_listings
		context['can_edit_item'] = False if user.is_anonymous else can_edit_listing(user, listing)
		context['can_delete_item'] = False if user.is_anonymous else can_delete_listing(user, listing)

		return context


class ItemListingDelete(GetObjectMixin, CanDeleteListingMixin, DeleteView):
	model = ItemListing
	success_url = reverse_lazy('marketplace:item-listing-list')


class ItemListingFilter(filters.FilterSet):
	title = filters.CharFilter(label=_('Item keywords'), method='filter_title')
	category = filters.ModelChoiceFilter(
		label=_('Category'),
		queryset=ItemCategory.objects.all(),
		method='filter_category'
	)

	class Meta:
		model = ItemListing
		fields = ['city', 'title', 'category', ]

	def __init__(self, *args, **kwargs):
		# set label for fields,
		# this is so as to enable translation of labels.
		super().__init__(*args, **kwargs)
		self.filters['city'].label = _('City')

	@property
	def qs(self):
		parent_qs = super().qs
		if country_code := self.request.session.get('country_code'):
			return parent_qs.filter(city__country__code=country_code)

		return parent_qs

	def filter_title(self, queryset, name, value):
		value_list = value.split()

		qs = queryset.filter(
			reduce(
				lambda x, y: x | y, 
				[Q(title__icontains=word) for word in value_list]
			)
		)
		return qs

	def filter_category(self, queryset, name, value):
		# `value` is the corresponding category instance
		return queryset.filter(sub_category__parent_category=value)


class ItemListingList(FilterView):
	model = ItemListing
	# context_object_name = 'listings'
	filterset_class = ItemListingFilter
	template_name = 'marketplace/itemlisting_list.html'
	# change the suffix coz by default FilterView expects '_filter'
	template_name_suffix = '_list'
	paginate_by = 7
	
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
		user, photos_list = request.user, request.session.get(user.username + AD_LISTING_SUFFIX, [])

		form_kwargs['user'] = user
		form_kwargs['country_or_code'] = request.session.get('country_code', user.country)
		form_kwargs['initial_photos'] = get_photos(photos_list, AD_PHOTOS_UPLOAD_DIR)
		return form_kwargs

	def form_valid(self, form):
		session, user = self.request.session, self.request.user
		self.object = form.save(commit=False)
		listing = self.object
		current_lang = get_language()

		## TRANSLATION
		if settings.ENABLE_GOOGLE_TRANSLATE:
			# get language to translate to
			trans_lang = 'fr' if current_lang == 'en' else 'en'

			translatable_fields = ['title', 'description', 'pricing', ]
			translate_fields = [field + '_' + trans_lang for field in translatable_fields]
			
			# fields that need to be translated. (see translation.py)
			# ommit slug because google corrects the slug to appropriate string b4 translating.
			# see demo in google translate .
			field_values = [getattr(listing, field) for field in translatable_fields]
			trans_results = translate_text(field_values, trans_lang)
			
			# each dict in trans_results contains keys: 
			# `input`, `translatedText`, `detectedSourceLanguage`
			for trans_field, result_dict in zip(translate_fields, trans_results):
				setattr(listing, trans_field, result_dict['translatedText'])

			# if object was saved in say english, slug_en will be set but not slug_fr. 
			# so get the slug in the other language
			# also, at this point, these attributes will be set(translated)
			if trans_lang == 'fr':
				listing.slug_fr = slugify(listing.title_fr)
			elif trans_lang == 'en':
				listing.slug_en = slugify(listing.title_en)

		with transaction.atomic():
			listing.poster = user
			listing.original_language = current_lang
			listing.save()
			listing.contact_numbers.add(*form.cleaned_data['contact_numbers'])

			# create photo instances pointing to the pre-created photos.
			photos_list = session.get(user.username + AD_LISTING_SUFFIX, []) 
			listing_photos = []
			for photo_name in photos_list:
				photo = AdListingPhoto()
				# path to file (relative path from MEDIA_ROOT)
				photo.file.name = os.path.join(AD_PHOTOS_UPLOAD_DIR, photo_name)
				listing_photos.append(photo)

			# bulk=False saves the photo instance before adding
			listing.photos.add(*listing_photos, bulk=False)

		# remove photos list from session 
		# pop() default is empty list since adverts mustn't have photos
		session.pop(user.username + AD_LISTING_SUFFIX, [])

		# Don't call the super() method here - you will end up saving the form twice. 
		# Instead handle the redirect yourself.
		return redirect(listing)


class AdListingUpdate(GetObjectMixin, CanEditListingMixin, UpdateView):
	form_class = AdListingForm
	model = AdListing
	template_name = 'marketplace/adlisting_update.html'

	def get_form_kwargs(self, **kwargs):
		form_kwargs, request = super().get_form_kwargs(**kwargs), self.request
		listing, user, session = self.object, request.user, request.session

		# when form is initially displayed, get photos from listing
		# otherwise(after form invalid) get photos from session.
		if request.method == 'GET':
			# store photos in session
			photos_list = [photo.actual_filename for photo in listing.photos.all()]

			# recall that photos are optional for adverts
			# so only update session if there are photos
			if photos_list:
				session[user.username + AD_LISTING_SUFFIX] = photos_list
		else:
			photos_list = session.get(user.username + AD_LISTING_SUFFIX, [])

		form_kwargs['user'] = user
		form_kwargs['country_or_code'] = request.session.get('country_code', user.country)
		form_kwargs['initial_photos'] = get_photos(photos_list, AD_PHOTOS_UPLOAD_DIR)
		form_kwargs['update'] = True
		return form_kwargs

	def form_valid(self, form):
		session, user = self.request.session, self.request.user
		listing = form.save(commit=False)
		changed_data = form.changed_data
		current_lang = get_language()

		if settings.ENABLE_GOOGLE_TRANSLATE:
			# get fields that are translatable(permitted to be translated)
			permitted_fields = ['title', 'description', 'pricing', ]

			updated_fields = [
				field for field in changed_data \
				if not field.endswith('_en') and not field.endswith('_fr')
			]
			desired_fields = [field for field in updated_fields if field in permitted_fields]

			trans_lang = 'fr' if current_lang == 'en' else 'en'

			# get and translated values that need to be translated
			field_values = [getattr(listing, field) for field in desired_fields]

			if field_values:
				trans_results = translate_text(field_values, trans_lang)
				
				# get fields that need to be set after translation
				translate_fields = [field + '_' + trans_lang for field in desired_fields]

				# each dict in trans_results contains keys: 
				# `input`, `translatedText`, `detectedSourceLanguage`
				for trans_field, result_dict in zip(translate_fields, trans_results):
					setattr(listing, trans_field, result_dict['translatedText'])

		with transaction.atomic():
			listing.update_language = current_lang	
			listing.save()
			listing.contact_numbers.set(form.cleaned_data['contact_numbers'], clear=True)

			# Update photos
			photos_list = session.get(user.username + AD_LISTING_SUFFIX, [])
			listing_photos = []

			# create photo instances pointing to the pre-created photos 
			# recall that these photos are already in the file system
			for photo_name in photos_list:
				photo = AdListingPhoto()
				# path to file (relative path from MEDIA_ROOT)
				photo.file.name = os.path.join(AD_PHOTOS_UPLOAD_DIR, photo_name)
				listing_photos.append(photo)

			listing.photos.set(listing_photos, bulk=False, clear=True)

		# remove photos list from session 
		session.pop(user.username + AD_LISTING_SUFFIX, [])

		# Don't call the super() method here - you will end up saving the form twice. 
		# Instead handle the redirect yourself.
		return redirect(listing)


class AdListingDetail(GetObjectMixin, IncrementViewCountMixin, DetailView):
	model = AdListing
	template_name = 'marketplace/adlisting_detail.html'
	context_object_name = 'listing'

	def get(self, request, *args, **kwargs):
		if should_redirect(object := self.get_object(), kwargs.get('slug')):
			return redirect(object, permanent=True)
		
		self.set_view_count()
		return super().get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		NUM_LISTINGS = 5
		user, listing = self.request.user, self.object
		context = super().get_context_data(**kwargs)
		
		similar_listings = AdListing.objects \
			.select_related('category', 'city__country') \
			.prefetch_related('photos') \
			.filter(city=listing.city, category=listing.category) \
			.exclude(id=listing.id) \
			.only('category', 'city', 'title', 'pricing', 'posted_datetime')[:NUM_LISTINGS]

		# get first photos of each similar listing
		first_photos = []
		# use a name other than 'listing' because of python's for loop scoping...
		for sim_listing in similar_listings:
			if sim_listing.photos.exists():
				first_photos.append(sim_listing.photos.first())
			else:
				first_photos.append(None)

		context['photos'] = listing.photos.all()
		context['contact_numbers'] = listing.contact_numbers.all()
		context['bookmarkers'] = listing.bookmarkers.only('id')
		context['similar_listings'] = similar_listings
		context['first_photos'] = first_photos
		context['can_edit_item'] = False if user.is_anonymous else can_edit_listing(user, listing)
		context['can_delete_item'] = False if user.is_anonymous else can_delete_listing(user, listing)
		
		return context


class AdListingDelete(GetObjectMixin, CanDeleteListingMixin, DeleteView):
	model = AdListing
	success_url = reverse_lazy('marketplace:ad-listing-list')


class AdListingFilter(filters.FilterSet):
	title = filters.CharFilter(label=_('Keywords'), method='filter_title')

	class Meta:
		model = AdListing
		fields = ['city', 'title', 'category', ]
	
	def __init__(self, *args, **kwargs):
		# set label for fields,
		# this is to enable translation of labels.
		super().__init__(*args, **kwargs)
		self.filters['city'].label = _('City')
		self.filters['category'].label = _('Category')

	@property
	def qs(self):
		parent_qs = super().qs
		if country_code := self.request.session.get('country_code'):
			return parent_qs.filter(
				Q(city__isnull=True) | Q(city__country__code=country_code)
			)

		return parent_qs

	def filter_title(self, queryset, name, value):
		value_list = value.split()
		qs = queryset.filter(
			reduce(
				lambda x, y: x | y, 
				[Q(title__icontains=word) for word in value_list]
			)
		)
		
		return qs


class AdListingList(FilterView):
	model = AdListing
	# context_object_name = 'listings'
	filterset_class = AdListingFilter
	template_name = 'marketplace/adlisting_list'
	template_name_suffix = '_list'
	paginate_by = 7
	
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

