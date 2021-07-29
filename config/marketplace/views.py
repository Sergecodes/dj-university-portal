from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from .forms import (
	ItemListingForm, 
	ItemListingPhotoFormset as ItemPhotoFormset
)
from .models import ItemListing


@login_required
def create_item_listing(request):
	user = request.user
	if POST := request.POST:
		# Sending user object to the form so as to display user's info
		listing_form = ItemListingForm(POST, user=user)
		photo_formset = ItemPhotoFormset(POST, request.FILES)

		if listing_form.is_valid() and photo_formset.is_valid():
			new_listing = listing_form.save(commit=False)
			new_listing.owner = user
			new_listing.institution = listing_form.cleaned_data['institution']
			new_listing.save()

			for photo_form in photo_formset:
				assert photo_form.is_valid(), 'Photo form in formset is invalid'

				listing_photo = photo_form.save(commit=False)
				listing_photo.item_listing = new_listing
				listing_photo.save()

			return HttpResponseRedirect('/')
		else:
			print(listing_form.errors, photo_formset.errors)
	else:
		listing_form = ItemListingForm(user=user)
		photo_formset = ItemPhotoFormset()
	
	return render(
		request, 
		'marketplace/listing_create.html', 
		{'form': listing_form, 'formset': photo_formset}
	)


'''
class ItemListingCreate(LoginRequiredMixin, CreateView):
	form_class = ItemListingForm
	model = ItemListing
	template_name = 'marketplace/listing_create.html'
	success_url = reverse_lazy('marketplace:listing-list')

	def post(self, request, *args, **kwargs):
		self.object = None   # set the itemlisting object to None for now.
		form = self.get_form()
		formset = ItemPhotoFormset(request.POST, request.FILES)

		# Now validate both the form and formset
		if form.is_valid() and formset.is_valid():
			return self.form_valid(form, formset)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, photo_formset):
		with transaction.atomic():
			self.object = form.save(commit=False)
			self.object.owner = self.request.user
			self.object.institution = form.cleaned_data['institution']
			self.object.save()
			new_listing = self.object

			for photo_form in photo_formset:
				assert photo_form.is_valid(), 'Photo form in formset is invalid'

				listing_photo = photo_form.save(commit=False)
				listing_photo.item_listing = new_listing
				listing_photo.save()
		
		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return HttpResponseRedirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)
		data['formset'] = ItemPhotoFormset(self.request.POST or None, self.request.FILES or None)
		return data
'''

class ItemListingList(ListView):
	model = ItemListing
	# paginate_by = 5
	

class ItemListingDetail(DetailView):
	model = ItemListing

