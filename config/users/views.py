from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator 
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models.query import Prefetch
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from core.constants import PHONE_NUMBERS_KEY
from qa_site.models import SchoolAnswer, AcademicAnswer
from socialize.views import HasSocialProfileMixin
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
		
		# remember, by default, `is_active` field on User model is False
		# so user won't be permitted to log in, even though his record exists in db
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
			_(
				'Please confirm your email address to complete the registration.'
				'You should receive a confirmation email anytime soon.'
			)
		)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		# add the phone_number formset to this view's context
		context['formset'] = PhoneNumberFormset(self.request.POST or None)
		return context


def activate_account(request, uidb64, token):
	"""Activate user account from email confirmation link"""
	try:
		uid = force_str(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	
	if user is not None and account_activation_token.check_token(user, token):
		# first retrieve(try to retrieve) phone numbers from session
		phone_numbers = request.session.pop(PHONE_NUMBERS_KEY, [])
		# phone numbers should normally be registered..
		if not phone_numbers:
			return HttpResponseBadRequest(_('No phone numbers registered.'))

		# since phone number is ok, register user.
		user.is_active = True
		# don't update only is_active field. other fields might also need updating
		# such as some datetime fields or django machinery stuff lol..
		user.save()

		# assign phone numbers to user
		for number_dict in phone_numbers:
			number = PhoneNumber(**number_dict)
			number.owner = user
			number.save()

		# send notifications(welcome-ish notifs) to new user
		User.objects.notify_new_user(user)
		login_url = reverse('users:login')

		return HttpResponse(
			_(
				'You have successfully confirmed your email. Now you can log into your account. <br>'
				'Login <a href="{login_url}">here</a>.'
			)
		)
	else:
		signup_url = reverse('users:register')
		return HttpResponse(
			_(
				'Activation link is invalid. <br>'
				'Please <a href="{signup_url}">sign up</a> again so as to get a new link.'
			)
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
		# print(form.fields)
		# print(request.POST)
		if request.POST.get('email'):
			# print("Email was sent, errror")
			form.add_error(
				'email', 
				ValidationError(_("You can't change your email address"))
			)

		if form.is_valid() and formset.is_valid():
			return self.form_valid(form, formset)
		else:
			# print(form.errors)
			# print(formset.errors)
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


### PROFILE TEMPLATES SECTIONS ###
class Dashboard(LoginRequiredMixin, TemplateView):
	template_name = "users/profile/dashboard.html"


class Marketplace(LoginRequiredMixin, TemplateView):
	template_name = "users/profile/marketplace.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user = self.request.user
		# include slug too since it is used to get the url of the object
		# also, for some unknown reason, the 'poster_id' field is requested.
		fields = ('id', 'title', 'posted_datetime', 'slug', 'poster_id', )

		context['item_listings'] = user.item_listings.only(*fields)
		context['ad_listings'] = user.ad_listings.only(*fields)
		context['bookmarked_items'] = user.bookmarked_item_listings.only(*fields)
		context['bookmarked_ads'] = user.bookmarked_ad_listings.only(*fields)
		
		return context


class QuestionsAndAnswers(LoginRequiredMixin, TemplateView):
	template_name = "users/profile/qa-site.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user = self.request.user
		all_users_id = User.objects.only('id')

		context['school_questions'] = user.school_questions.select_related('school').prefetch_related(
			Prefetch('upvoters', queryset=all_users_id),
			Prefetch('downvoters', queryset=all_users_id),
			Prefetch('answers', queryset=SchoolAnswer.objects.only('id'))
		)
		context['academic_questions'] = user.academic_questions.prefetch_related(
			Prefetch('upvoters', queryset=all_users_id),
			Prefetch('downvoters', queryset=all_users_id),
			Prefetch('answers', queryset=AcademicAnswer.objects.only('id'))
		)

		qstn_fields = ('id', 'poster_id', 'posted_datetime', )
		ans_fields = ('id', 'content', 'posted_datetime', 'question_id', 'poster_id', )
		context['bookmarked_academic_qstns'] = user.bookmarked_academic_questions \
			.only('title', *qstn_fields)
		context['bookmarked_school_qstns'] = user.bookmarked_school_questions \
			.only('content', *qstn_fields)

		context['academic_answers'] = user.academic_answers.only('question__slug', *ans_fields)
		context['school_answers'] = user.school_answers.only(*ans_fields)

		return context


class LostAndFound(LoginRequiredMixin, TemplateView):
	template_name = "users/profile/lost-or-found.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user = self.request.user
		fields = ('id', 'slug', 'posted_datetime', 'poster_id', )

		context['lost_items'] = user.lost_items.only('item_lost', *fields)
		context['found_items'] = user.found_items.only('item_found', *fields)
		context['bookmarked_lost_items'] = user.bookmarked_lost_items.only('item_lost', *fields)
		context['bookmarked_found_items'] = user.bookmarked_found_items.only('item_found', *fields)
		return context


class RequestedItems(LoginRequiredMixin, TemplateView):
	template_name = "users/profile/requested-items.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user = self.request.user
		fields = ('id', 'slug', 'item_requested', 'posted_datetime', 'poster_id', )

		context['requested_items'] = user.requested_items.only(*fields)
		context['bookmarked_requested_items'] = user.bookmarked_requested_items.only(*fields)
		return context


class PastPaper(LoginRequiredMixin, TemplateView):
	template_name = "users/profile/past-papers.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user = self.request.user
		fields = ('id', 'title', 'slug', 'posted_datetime', 'poster_id', )

		context['past_papers'] = user.past_papers.only(*fields)
		context['bookmarked_past_papers'] = user.bookmarked_past_papers.only(*fields)
		return context


class BookmarkedSocialProfiles(LoginRequiredMixin, HasSocialProfileMixin, TemplateView):
	template_name = "users/profile/bookmarked-profiles.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user = self.request.user
		fields = ('user_id', 'user__username', 'user__full_name' )
		context['bookmarked_profiles'] = user.bookmarked_social_profiles.only(*fields)

		return context


# Override auth views by redirecting user to appropriate page if he isn't logged in.
# class UserLogin(auth_views.LoginView):
# 	"""Redirect user to home page if he's already logged in."""
# 	def get(self, request, *args, **kwargs):
# 		if request.user.is_authenticated:
# 			return redirect('/')

# 		return super().get(request, *args, **kwargs)
	


