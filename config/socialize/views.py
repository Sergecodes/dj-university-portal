from datetime import timedelta, timezone
import django_filters as filters
from django_filters.views import FilterView
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django import forms
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View 
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from marketplace.models import Institution
from past_papers.models import PastPaper
from .forms import SocialProfileForm, SocialMediaFollowForm
from .models import SocialProfile, SocialMediaFollow

User = get_user_model()


class SocialProfileCreate(LoginRequiredMixin, View):
	template_name = 'socialize/socialprofile_form.html'

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {
			'profile_form': SocialProfileForm(),
			'media_form': SocialMediaFollowForm()
		})

	def post(self, request, *args, **kwargs):
		social_profile_form = SocialProfileForm(request.POST, request.FILES)
		social_media_form = SocialMediaFollowForm(request.POST)
		
		if social_profile_form.is_valid() and social_media_form.is_valid():
			social_media = social_media_form.save()
			social_profile = social_profile_form.save(commit=False)
			social_profile.user = request.user
			social_profile.social_media = social_media
			social_profile.save()
			
			return HttpResponseRedirect('/')

		return render(request, self.template_name, {
			'profile_form': social_profile_form,
			'media_form': social_media_form
		})


class SocialProfileUpdate(UserPassesTestMixin, View):
	template_name = 'socialize/socialprofile_update_form.html'
	
	def is_valid_user(self):
		"""
		Permit access to logged in users whose username matches with that passed in the url and who have social profiles.
		If no match, 403 Forbidden is raised.
		"""
		passed_username = self.kwargs.get('username', '')
		user = self.request.user

		if user.username == passed_username and user.social_profile:
			return True

		return False

	def get_test_func(self):
		# should return a function (not a call to a function) hence no parentheses
		return self.is_valid_user

	def get(self, request, *args, **kwargs):
		# this will always be non-null coz there's a text to ensure only user's with social profiles can access these methods
		object = request.user.social_profile

		return render(request, self.template_name, {
			'profile_form': SocialProfileForm(instance=object),
			'media_form': SocialMediaFollowForm(instance=object.social_media)
		})
	
	def post(self, request, *args, **kwargs):
		POST, object = request.POST, request.user.social_profile
		social_profile_form = SocialProfileForm(POST, request.FILES, instance=object)
		social_media_form = SocialMediaFollowForm(POST, instance=object.social_media)
		
		if social_profile_form.is_valid() and social_media_form.is_valid():
			social_media = social_media_form.save()
			social_profile = social_profile_form.save(commit=False)
			# no need to update the user since it's the same user instance
			# social_profile.user = request.user
			social_profile.social_media = social_media
			social_profile.save()
			
			return HttpResponseRedirect('/')

		return render(request, self.template_name, {
			'profile_form': SocialProfileForm(POST, instance=object),
			'media_form': SocialMediaFollowForm(POST, instance=object.social_media)
		})


class SocialProfileFilter(filters.FilterSet):
	# filter used to filter social profiles
	# if you change this tuple, don't forget to review the `filter_age` method.
	AGE_CHOICES = (
		(0, _('Any Age')),
		(1, _('15 Below')),
		(2, _('16 - 19')),
		(3, _('20 - 25')), 
		(4, _('26 - 29')),
		(5, _('30 Above')),
	)

	GENDERS = (
		('M', _('A guy')),
		('F', _('A lady'))
	)

	LANGUAGE_CHOICES = (
		('en', _('English speaking')),
		('fr', _('French speaking'))
	)

	name = filters.CharFilter(
		field_name='user__full_name', 
		label=_('Search by name:'), 
		lookup_expr='icontains'
	)
	gender = filters.MultipleChoiceFilter(
		widget=forms.CheckboxSelectMultiple(),
		choices=GENDERS,
		label=_("I'm searching for:"),
		method='filter_gender'
	)
	main_language = filters.MultipleChoiceFilter(
		label=_('Principal language'),
		widget=forms.CheckboxSelectMultiple(),
		choices=LANGUAGE_CHOICES,
		method='filter_language',
	)
	age = filters.ChoiceFilter(
		label=_('Between the age of:'), 
		method='filter_age',
		empty_label=None,
		choices=AGE_CHOICES
	)
	school = filters.ModelChoiceFilter(
		empty_label=_('All schools'),
		queryset=Institution.objects.all()
	)
	level = filters.ChoiceFilter(
		label=_('At the level of:'),
		choices=PastPaper.LEVELS,
		empty_label=_('Any level')
	)
	interest = filters.ChoiceFilter(
		label=_('With special interest in:'),
		choices=SocialProfile.INTERESTED_RELATIONSHIPS,
		empty_label=_('Anything')
	)
	has_profile_image = filters.BooleanFilter(
		widget=forms.CheckboxInput(),
		label=_('Must have profile image'),
		method='filter_dp',
		help_text=_('<br>Note that most users do not have profile images')
	)

	class Meta:
		model = SocialProfile
		fields = [
			'name', 'school', 'gender', 
			'main_language', 'age', 'level', 
			'interest', 'has_profile_image', 
		]	

	def filter_language(self, queryset, name, value):
		# value will be a list containing the selected values
		# also note that if a value for a given field isn't entered (for this MultipleChoiceFilter), it's filter method isn't run. cool.
		return queryset.filter(user__first_language__in=value)		
	
	def filter_age(self, queryset, name, value):
		now = timezone.now()

		# don't fret, querysets are lazy
		lookup = {
			0: queryset,
			1: queryset.filter(birth_date__gte=(now-timedelta(days=15*365)).date()),
			2: queryset.filter(
					birth_date__range=(
						# note the 19 comes before 16(due to the subtraction...)
						(now-timedelta(days=19*365)).date(),
						(now-timedelta(days=16*365)).date()
					)
				),
			3: queryset.filter(
					birth_date__range=(
						(now-timedelta(days=25*365)).date(),
						(now-timedelta(days=20*365)).date()
					)
				),
			4: queryset.filter(
					birth_date__range=(
						(now-timedelta(days=29*365)).date(),
						(now-timedelta(days=26*365)).date()
					)
				),
			5: queryset.filter(birth_date__lte=(now-timedelta(days=30*365)).date()),
		}
		
		return lookup[int(value)]

	def filter_dp(self, queryset, name, value):
		# if user wants profiles with dp
		if value:
			return queryset.filter(profile_image__isnull=False)
		return queryset

	def filter_gender(self, queryset, name, value):
		return queryset.filter(gender__in=value)

	@property
	def qs(self):
		parent = super().qs
		# order results also to ensure consistent results for pagination as warned by django
		return parent.order_by('-user__site_points')


@login_required
def friend_finder(request):
	NUM_USERS = 7

	if not request.user.social_profile:
		return redirect(reverse('socialize:create-profile'))	

	# use empty queryset since we won't be displaying any results on this template.
	filter = SocialProfileFilter(request.GET, queryset=SocialProfile.objects.none())

	# todo get users with most points seven days ago.  
	# create function in user model and cache this for a given period...
	best_users = SocialProfile.objects.order_by('-user__site_points')[:NUM_USERS]

	context = {
		'filter': filter,
		'best_users': best_users
	}

	return render(request, 'socialize/socialprofile_filter.html', context)


class SocialProfileList(LoginRequiredMixin, FilterView):
	## List of filtered social profile results
	model = SocialProfile
	# context_object_name = 'social_profiles'
	filterset_class = SocialProfileFilter
	template_name = 'socialize/socialprofile_list.html'
	template_name_suffix = '_list'
	paginate_by = 2

	def get_context_data(self, **kwargs):
		NUM_USERS = 7
		context = super().get_context_data(**kwargs)

		# todo; get best users for given week
		# for now, just get all users...
		context['best_users'] = SocialProfile.objects.order_by('-user__site_points')[:NUM_USERS]

		return context
