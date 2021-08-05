# import bleach
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
# from django.utils.html import escape
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from core.constants import (
	LISTING_PHOTOS_UPLOAD_DIRECTORY, 
	MIN_LISTING_PHOTOS_LENGTH
)
from .forms import (
	ItemListingForm, 
)
from .models import (
	ItemListing, ItemCategory, 
	ItemListingPhoto
)


class ItemListingCreate(LoginRequiredMixin, CreateView):
	form_class = ItemListingForm
	model = ItemListing
	template_name = 'marketplace/listing_create.html'
	success_url = reverse_lazy('marketplace:listing-list')

	def get_form_kwargs(self, **kwargs):
		form_kwargs = super().get_form_kwargs(**kwargs)
		form_kwargs['user'] = self.request.user
		return form_kwargs

	def get(self, request, *args, **kwargs):
		# remove photos list from session (just in case...)
		request.session.pop(request.user.username, '')
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
			# remove and return photos list from session 
			photos_list = request.session.pop(request.user.username, [])

			# delete uploaded photos(and also remove corresponding files)
			# no need to delete photos. this will cause unneccessary load on server. instead, just allow the photos, but regularly remove photos not linked to model instances.
			for photo_name in photos_list:
				# todo code to delete file here..
				pass

			print(form.errors)
			return self.form_invalid(form)

	def form_valid(self, form):
		request = self.request
		session, username = request.session, request.user.username
		self.object = form.save(commit=False)
		listing = self.object
		listing.owner = request.user
		listing.institution = form.cleaned_data['institution']
		listing.save()

		photos_list = session.get(username, [])  # get list of photo names
		assert len(photos_list) >= MIN_LISTING_PHOTOS_LENGTH, 'There should be at least 3 photos'
		
		# create photo instances pointing to the pre-created photos.
		print(photos_list)
		for photo_name in photos_list:
			photo = ItemListingPhoto()
			# path to file (relative path from MEDIA_ROOT)
			photo.file.name = LISTING_PHOTOS_UPLOAD_DIRECTORY + photo_name
			listing.photos.add(photo, bulk=False)  # bulk=False saves the photo instance before adding

		# remove photos list from session 
		request.session.pop(request.user.username)

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		# return HttpResponseRedirect(self.get_success_url())
		return HttpResponseRedirect('/')

@login_required
def create_item_listing(request):
	user = request.user

	if POST := request.POST:
		# Sending user object to the form so as to display user's info
		listing_form = ItemListingForm(POST, user=user)

		if listing_form.is_valid():
			new_listing = listing_form.save(commit=False)
			new_listing.owner = user
			new_listing.institution = listing_form.cleaned_data['institution']
			# new_listing.save()

			return HttpResponseRedirect('/')
		else:
			print(listing_form.errors)
	else:
		listing_form = ItemListingForm(user=user)
	
	return render(
		request, 
		'marketplace/listing_create.html', 
		{'form': listing_form}
	)

class ItemListingList(ListView):
	model = ItemListing
	# paginate_by = 5
	

class ItemListingDetail(DetailView):
	model = ItemListing

