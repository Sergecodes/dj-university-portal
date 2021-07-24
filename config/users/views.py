from django.contrib.auth import (
	authenticate, 
	login, 
	logout,
	get_user_model
)
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.views import logout_then_login
from django.db import transaction
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView

from .forms import PhoneNumberFormset, UserCreationForm, UserChangeForm

User = get_user_model()

class UserCreate(CreateView):
	model = User
	form_class = UserCreationForm
	template_name = 'users/auth/signup.html'
	success_url = '/'

	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		
		formset = PhoneNumberFormset(request.POST)

		# Now validate both the form and formset
		if form.is_valid() and formset.is_valid():
			return self.form_valid(form, formset)
		else:
			return self.form_invalid(form)

	def get(self, request, *args, **kwargs):
		"""
		Prevent currently logged in users from calling the register method without logging out.
		i.e. only unauthed users can access this view..
		"""
		# just for testing, don't forget to remove this.
		if request.user.is_authenticated and request.user.username == 'sergeman':
			return super().get(request, *args, **kwargs)

		if request.user.is_authenticated:
			return redirect('/')

		return super().get(request, *args, **kwargs)

	def form_valid(self, form, phone_number_formset):
		# this method is called when the form has been successfully validated
		request = self.request
		email, password = form.cleaned_data['email'], form.cleaned_data['password']

		with transaction.atomic():
			self.object = form.save()
			formset = phone_number_formset

			# Now we process the phone number formset
			phone_numbers = formset.save(commit=False)

			for phone_number in phone_numbers:
				# phone_number.instance = self.object
				phone_number.owner = self.object
				phone_number.save()
		
		# log new user in
		user = authenticate(request, email=email, password=password)
		assert user is not None

		login(request, user)

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return HttpResponseRedirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)

		# add the phone_number formset to this view's context
		data['formset'] = PhoneNumberFormset(self.request.POST or None)
		return data


class UserUpdate(UserPassesTestMixin, UpdateView):
	model = User
	form_class = UserChangeForm
	slug_url_kwarg = "username"
	slug_field = "username"
	template_name = 'users/auth/edit_profile.html'
	# success_url = reverse_url('users:view-profile')

	def username_matches(self):
		"""
		Permit access to logged in users whose username matches with that passed in the url.
		If no match, 403 Forbidden is raised.
		"""
		passed_username = self.kwargs.get('username')
		return self.request.user.username == passed_username

	def get_test_func(self):
		return self.username_matches

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		form = self.get_form()
		formset = PhoneNumberFormset(request.POST, instance=self.object)

		# if form.is_valid():
		# 	print(form.cleaned_data)

		if form.is_valid() and formset.is_valid():
			return self.form_valid(form, formset)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, phone_number_formset):
		with transaction.atomic():
			self.object = form.save()
			formset = phone_number_formset

			# Now we process the phone number formset
			# also remove those that were marked to be deleted
			phone_numbers = formset.save(commit=False)
			
			for phone_number in phone_numbers:
				phone_number.owner = self.object
				phone_number.save()

		# Don't call the super() method here - you will end up saving the form twice. 
		# Instead handle the redirect yourself.
		return HttpResponseRedirect(reverse('users:view-profile', kwargs={'username': self.object.username}))
		# return HttpResponseRedirect('/')
		# return HttpResponseRedirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)
		
		if POST := self.request.POST:
			data['formset'] = PhoneNumberFormset(POST, instance=self.object)
		else:
			data['formset'] = PhoneNumberFormset(instance=self.object)

		return data


class UserDetail(DetailView):
	model = User
	slug_url_kwarg = "username"
	slug_field = "username"
	template_name = 'users/view_profile.html'


def logout_and_login(request):
	"""Logout the redirect user to login page."""
	return logout_then_login(request)

# Override auth views by redirecting user to appropriate page if he isn't logged in.
# class UserLogin(auth_views.LoginView):
# 	"""Redirect user to home page if he's already logged in."""
# 	def get(self, request, *args, **kwargs):
# 		if request.user.is_authenticated:
# 			return redirect('/')

# 		return super().get(request, *args, **kwargs)
	


