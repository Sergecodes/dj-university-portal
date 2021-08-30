from users.models import PhoneNumber
from django.contrib.auth import (
	authenticate, 
	login, 
	logout,
	get_user_model
)
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.views import logout_then_login
from django.core.exceptions import ValidationError
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView

from .forms import (
	PhoneNumberFormset, EditPhoneNumberFormset,
	UserCreationForm, UserUpdateForm
)

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
		# just for testing, don't forget to remove this.  todo
		if request.user.is_authenticated and request.user.username == 'sergeman':
			return super().get(request, *args, **kwargs)

		if request.user.is_authenticated:
			return redirect('/')

		return super().get(request, *args, **kwargs)

	def form_valid(self, form, phone_number_formset):
		# this method is called when the form has been successfully validated
		request = self.request

		# with transaction.atomic():
		self.object = form.save()
		new_user = self.object
		
		for number_form in phone_number_formset:
			phone_number = number_form.save(commit=False)
			phone_number.owner = new_user
			phone_number.save()
		
		# log new user in
		login(request, new_user)

		# Don't call the super() method here - you will end up saving the form twice. Instead handle the redirect yourself.
		return HttpResponseRedirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)

		# add the phone_number formset to this view's context
		data['formset'] = PhoneNumberFormset(self.request.POST or None)
		return data


class UserUpdate(UserPassesTestMixin, UpdateView):
	model = User
	form_class = UserUpdateForm
	slug_url_kwarg = 'username'
	slug_field = 'username'
	template_name = 'users/edit_profile.html'
	# success_url = reverse_url('users:view-profile')

	def username_matches(self):
		"""
		Permit access to logged in users whose username matches with that passed in the url.
		If no match, 403 Forbidden is raised.
		"""
		passed_username = self.kwargs.get('username', '')
		return self.request.user.username == passed_username

	def get_test_func(self):
		return self.username_matches

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		form = self.get_form()
		formset = EditPhoneNumberFormset(request.POST, instance=self.object)

		if form.is_valid() and formset.is_valid():
			return self.form_valid(form, formset)
		else:
			print(form.errors)
			print(formset.errors)
			return self.form_invalid(form)

	def form_valid(self, form, phone_number_formset):
		# with transaction.atomic():
		self.object = form.save()
		user = self.object
		
		# remove all previous numbers
		user.phone_numbers.all().delete()
		
		for number_form in phone_number_formset:
			phone_number = number_form.save(commit=False)
			phone_number.owner = user
			phone_number.save()
		# print(user.phone_numbers.all())

		# Don't call the super() method here - you will end up saving the form twice. 
		# Instead handle the redirect yourself.
		return HttpResponseRedirect(reverse('users:view-profile', kwargs={'username': user.username}))
		# return HttpResponseRedirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)
		
		if POST := self.request.POST:
			data['formset'] = EditPhoneNumberFormset(POST, instance=self.object)
		else:
			data['formset'] = EditPhoneNumberFormset(instance=self.object)

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
	


