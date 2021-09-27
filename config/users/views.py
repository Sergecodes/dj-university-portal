from django.contrib.auth import (
	authenticate, 
	login, 
	logout,
	get_user_model
)
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.views import logout_then_login
from django.db.models.query import Prefetch
from django.http.response import HttpResponseRedirect
from django.shortcuts import  redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from qa_site.models import SchoolAnswer, AcademicAnswer
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


class UserUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = User
	form_class = UserUpdateForm
	slug_url_kwarg = 'username'
	slug_field = 'username'
	template_name = 'users/edit_profile.html'
	# success_url = reverse_url('users:view-profile')

	def test_func(self):
		# Permit access only to current user 
		# note that we can't permit access to staff too because he will instead be 
		# trying to edit his own profile...
		user = self.request.user
		passed_username = self.kwargs.get('username')
		return user.username == passed_username

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
		user.phone_numbers.clear()
		
		for number_form in phone_number_formset:
			phone_number = number_form.save(commit=False)
			phone_number.owner = user
			phone_number.save()
		# print(user.phone_numbers.all())

		# Don't call the super() method here - you will end up saving the form twice. 
		# Instead handle the redirect yourself.
		return HttpResponseRedirect(user.get_absolute_url())
		# return HttpResponseRedirect(reverse('users:view-profile', kwargs={'username': user.username}))
		# return HttpResponseRedirect(self.get_success_url())

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['formset'] = EditPhoneNumberFormset(
			self.request.POST or None, 
			instance=self.object
		)
		return context


def logout_and_login(request):
	"""Logout the redirect user to login page."""
	return logout_then_login(request)


### PROFILE TEMPLATES SECTIONS ###

class Dashboard(LoginRequiredMixin, TemplateView):
	template_name = "users/profile/dashboard.html"
	# todo add notifications to context... to this page.


class Marketplace(LoginRequiredMixin, TemplateView):
	template_name = "users/profile/marketplace.html"


class QuestionsAndAnswers(LoginRequiredMixin, TemplateView):
	template_name = "users/profile/qa-site.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user, all_users = self.request.user, User.objects.all()

		user_school_questions = user.school_questions.select_related('school').prefetch_related(
			Prefetch('upvoters', queryset=all_users.only('id')),
			Prefetch('downvoters', queryset=all_users.only('id')),
			Prefetch('answers', queryset=SchoolAnswer.objects.all().only('id'))
		)
		user_academic_questions = user.academic_questions.prefetch_related(
			Prefetch('upvoters', queryset=all_users.only('id')),
			Prefetch('downvoters', queryset=all_users.only('id')),
			Prefetch('answers', queryset=AcademicAnswer.objects.all().only('id'))
		)

		context['school_questions'] = user_school_questions
		context['academic_questions'] = user_academic_questions
		return context


class LostAndFound(LoginRequiredMixin, TemplateView):
	template_name = "users/profile/lost-and-found.html"


class RequestedItems(LoginRequiredMixin, TemplateView):
	template_name = "users/profile/requested-items.html"


class PastPaper(LoginRequiredMixin, TemplateView):
	template_name = "users/profile/past-papers.html"


# class MyProfile(LoginRequiredMixin, DetailView):
# 	model = User
# 	template_name = 'users/profile/dashboard.html'

# 	def get_object(self, queryset=None):
# 		return self.request.user
	

# Override auth views by redirecting user to appropriate page if he isn't logged in.
# class UserLogin(auth_views.LoginView):
# 	"""Redirect user to home page if he's already logged in."""
# 	def get(self, request, *args, **kwargs):
# 		if request.user.is_authenticated:
# 			return redirect('/')

# 		return super().get(request, *args, **kwargs)
	


