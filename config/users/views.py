from django.conf import settings
from django.contrib.auth import (
	authenticate, login, logout,
	get_user_model
)
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator 
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.views import logout_then_login
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models.query import Prefetch
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from core.constants import PHONE_NUMBERS_KEY
from qa_site.models import SchoolAnswer, AcademicAnswer
from users.models import PhoneNumber
from .forms import (
	PhoneNumberFormset, EditPhoneNumberFormset,
	UserCreationForm, UserUpdateForm
)

account_activation_token = PasswordResetTokenGenerator()
User = get_user_model()


class UserCreate(CreateView):
	model = User
	form_class = UserCreationForm
	template_name = 'users/auth/signup.html'
	success_url = '/'

	def get(self, request, *args, **kwargs):
		"""
		Prevent currently logged in users from calling the register method without logging out.
		i.e Redirect them to index page.
		Only unauthed users can access this method..
		"""
		# just for testing, don't forget to remove this super user stuff.  TODO
		if request.user.is_authenticated and request.user.is_superuser:
			return super().get(request, *args, **kwargs)

		if request.user.is_authenticated:
			return redirect('/')

		return super().get(request, *args, **kwargs)
		
	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		formset = PhoneNumberFormset(request.POST)
		
		# Now validate both the form and formset
		if form.is_valid() and formset.is_valid():
			return self.form_valid(form, formset)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, phone_number_formset):
		# this method is called when the form has been successfully validated
		# also accounts for sending confirmation email to user.
		
		request, new_user = self.request, form.save()
		
		# compose and send email verification mail
		mail_subject = _('Activate your account')
		message = render_to_string('users/auth/email_confirm.html', {
			'user': new_user,
			'domain': get_current_site(request).domain,
			'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
			'token': account_activation_token.make_token(new_user)
		})
		to_email = new_user.email
		send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
		
		# store phone numbers in session
		phone_numbers_list = []
		for number_form in phone_number_formset:
			phone_number = number_form.save(commit=False)
			phone_number_dict = {
				'operator': phone_number.operator,
				'number': phone_number.number,
				'can_whatsapp': phone_number.can_whatsapp
			}
			phone_numbers_list.append(phone_number_dict)

		request.session[PHONE_NUMBERS_KEY] = phone_numbers_list

		return HttpResponse(
			_('Please confirm your email address to complete the registration')
		)

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)

		# add the phone_number formset to this view's context
		data['formset'] = PhoneNumberFormset(self.request.POST or None)
		return data


def activate_account(request, uidb64, token):
	"""Activate user account from email confirmation link"""
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	
	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.save()

		# retrieve phone numbers from session and assign to user
		phone_numbers = request.session.pop(PHONE_NUMBERS_KEY, [])
		if not phone_numbers:
			return HttpResponseBadRequest(_('No phone numbers registered.'))

		for number_dict in phone_numbers:
			number = PhoneNumber(**number_dict)
			number.owner = user
			number.save()

		# send notifications(welcome-ish notifs) to new user
		User.objects.notify_new_user(user)

		return HttpResponse(
			_('You have successfully confirmed your email. Now you can log into your account')
		)
	else:
		return HttpResponse(
			_('Activation link is invalid. Sign up again so as to get a new link.')
		)


class UserUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = User
	form_class = UserUpdateForm
	slug_url_kwarg = 'username'
	slug_field = 'username'
	template_name = 'users/edit_profile.html'
	permission_denied_message = _('This is not your username. You can only edit your own account.')

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

		# ensure email wasn't sent(email should not be in the form)
		# email is included in list of form fields (UserUpdateForm),
		# but it's marked disabled so it shouldn't be sent.
		# it will be gotten from the object instance
		# frontend prevention is done and this is for backend
		print(form.fields)
		print(request.POST)
		if request.POST.get('email'):
			print("Email was sent")
			form.add_error(
				'email', 
				ValidationError(_("You can't change your email address"))
			)
		else:
			print("All good, no email sent.")

		if form.is_valid() and formset.is_valid():
			return self.form_valid(form, formset)
		else:
			print(form.errors)
			print(formset.errors)
			if not form.is_valid():
				return self.form_invalid(form)
			if not formset.is_valid():
				return self.form_invalid(formset)

	def form_valid(self, form, phone_number_formset):
		# with transaction.atomic():
		self.object = form.save()
		user = self.object
		
		# remove all previous numbers
		# no clear() method available coz null is not = True for this field
		user.phone_numbers.all().delete()
		
		for number_form in phone_number_formset:
			phone_number = number_form.save(commit=False)
			phone_number.owner = user
			phone_number.save()
			# save many2many fields since the form was saved with commit=False
			number_form.save_m2m()

		# Don't call the super() method here - you will end up saving the form twice. 
		# Instead handle the redirect yourself.
		return redirect(user.get_absolute_url())

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['formset'] = EditPhoneNumberFormset(
			self.request.POST or None, 
			instance=self.object
		)
		return context


# def logout_and_login(request):
# 	"""Logout then redirect user to login page."""
# 	return logout_then_login(request)


### PROFILE TEMPLATES SECTIONS ###

class Dashboard(LoginRequiredMixin, TemplateView):
	template_name = "users/profile/dashboard.html"


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
	


