import copy
import django_filters as filters
from datetime import timedelta, timezone
from django import forms
from django_filters.views import FilterView
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import get_language, gettext_lazy as _
from django.views import View 
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView
from django.views.generic.base import TemplateView

from core.mixins import IncrementViewCountMixin
from core.models import Institution
from core.utils import get_random_profiles, translate_text
from past_papers.models import PastPaper
from .forms import SocialProfileForm, SocialMediaFollowForm
from .models import SocialProfile

User = get_user_model()


def has_social_profile(user):
	"""Verify if user has social profile"""
	return user.has_social_profile


class HasSocialProfileMixin(UserPassesTestMixin):
	login_url = reverse_lazy('socialize:create-profile')

	def test_func(self):
		return has_social_profile(self.request.user)


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

			## TRANSLATION
			# get current language and language to translate to
			current_lang = get_language()
			trans_lang = 'fr' if current_lang == 'en' else 'en'

			translatable_fields = ['speciality', 'about_me', 'hobbies', ]
			translate_fields = [field + '_' + trans_lang for field in translatable_fields]
			
			# fields that need to be translated. (see translation.py)
			# omit slug because google corrects the slug to appropriate string b4 translating.
			# see demo in google translate .
			field_values = [getattr(social_profile, field) for field in translatable_fields]
			trans_results = translate_text(field_values, trans_lang)
			
			# each dict in trans_results contains keys: 
			# `input`, `translatedText`, `detectedSourceLanguage`
			for trans_field, result_dict in zip(translate_fields, trans_results):
				setattr(social_profile, trans_field, result_dict['translatedText'])

			social_profile.user = request.user
			social_profile.social_media = social_media
			social_profile.original_language = current_lang
			social_profile.save()
			
			return redirect(social_profile)
			
		return render(request, self.template_name, {
			'profile_form': social_profile_form,
			'media_form': social_media_form
		})


class SocialProfileUpdate(LoginRequiredMixin, UserPassesTestMixin, View):
	template_name = 'socialize/socialprofile_update_form.html'

	def test_func(self):
		"""
		Restrict access to only users whose username is the current username 
		and user should have a social profile.
		"""
		user, passed_username = self.request.user, self.kwargs.get('username')
		if user.username == passed_username and user.has_social_profile:
			return True
			
		return False

	def get_login_url(self):
		user = self.request.user

		if user.is_anonymous:
			return reverse('users:login')

		if not user.has_social_profile:
			return reverse('socialize:create-profile')

		return super().get_login_url()

	def get_permission_denied_message(self):
		user, passed_username = self.request.user, self.kwargs.get('username')
		if user.username != passed_username:
			return _('You can only update your own profile')

		# if username is user's but he doesn't have a social profile
		if not user.has_social_profile():
			return _("You don't have a social profile ")
			
		return super().get_permission_denied_message()

	def get(self, request, *args, **kwargs):
		# this will always be non-null coz there's a test 
		# to ensure only users with social profiles can access these methods
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

			## TRANSLATION
			changed_data = social_profile_form.changed_data

			# get fields that are translatable(permitted to be translated)
			permitted_fields = ['speciality', 'about_me', 'hobbies', ]

			updated_fields = [
				field for field in changed_data if \
				not field.endswith('_en') and not field.endswith('_fr')
			]
			desired_fields = [field for field in updated_fields if field in permitted_fields]

			current_lang = get_language()
			trans_lang = 'fr' if current_lang == 'en' else 'en'

			# get and translated values that need to be translated
			field_values = [getattr(social_profile, field) for field in desired_fields]
			trans_results = translate_text(field_values, trans_lang)
			
			# get fields that need to be set after translation
			translate_fields = [field + '_' + trans_lang for field in desired_fields]

			# each dict in trans_results contains keys: 
			# `input`, `translatedText`, `detectedSourceLanguage`
			for trans_field, result_dict in zip(translate_fields, trans_results):
				setattr(social_profile, trans_field, result_dict['translatedText'])

			social_profile.social_media = social_media
			social_profile.update_language = current_lang
			social_profile.save()
			
			return redirect(social_profile)

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

	# get interested relations (do not include `not interested`.)
	interested_relations = copy.deepcopy(SocialProfile.INTERESTED_RELATIONSHIPS)
	interested_relations.pop(0)

	name = filters.CharFilter(
		field_name='user__full_name', 
		label=_('Search by name:'), 
		lookup_expr='icontains'
	)
	gender = filters.ChoiceFilter(
		widget=forms.RadioSelect(),
		choices=GENDERS,
		label=_("I'm searching for:"),
		method='filter_gender',
		empty_label=_('Any')
	)
	main_language = filters.ChoiceFilter(
		label=_('Principal language'),
		widget=forms.RadioSelect(),
		choices=LANGUAGE_CHOICES,
		method='filter_language',
		empty_label=_('Any')
	)
	age = filters.ChoiceFilter(
		label=_('Between the age of:'), 
		method='filter_age',
		empty_label=None,
		choices=AGE_CHOICES,
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
		choices=interested_relations,
		empty_label=_('Anything'),
		method='filter_interest'
	)
	has_profile_image = filters.BooleanFilter(
		widget=forms.CheckboxInput(),
		label=_('Must have profile image'),
		method='filter_dp',
		help_text=_('<br>Most users do not have a profile image')
	)

	class Meta:
		model = SocialProfile
		fields = [
			'name', 'school', 'gender', 'main_language', 'age', 
			'level', 'interest', 'has_profile_image', 
		]	

	def filter_language(self, queryset, name, value):
		# value will be a list containing the selected values
		# also note that if a value for a given field isn't entered (for this MultipleChoiceFilter),
		# it's filter method isn't run. cool.
		
		return queryset.filter(user__first_language=value)		
	
	def filter_age(self, queryset, name, value):
		# passed age should be coercible to an integer
		# else don't filter(return same queryset)
		try:
			value = int(value)
		except ValueError:
			return queryset

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
		
		return lookup[value]

	def filter_dp(self, queryset, name, value):
		# if user wants profiles with dp
		if value:
			return queryset.filter(profile_image__isnull=False)
		return queryset

	def filter_gender(self, queryset, name, value):
		# don't bother filtering if gender is invalid
		if value not in ('M', 'F'):
			return queryset
		return queryset.filter(gender=value)

	def filter_interest(self, queryset, name, value):
		# if no value was passed (if user is filtering by 'Anything')
		# exclude users that set this field to 'Not interested'. (val = 'none')
		# even if 'none' is passed, exclude these users.
		# see model SocialProfile.INTERESTED_RELATIONSHIPS
		if not value or value == 'none':
			return queryset.exclude(interested_relationship='none')
		else:
			return queryset.filter(interested_relationship=value)

	@property
	def qs(self):
		parent = super().qs
		# order results by user points
		return parent.order_by('-user__site_points')


class SocialProfileDetail(
		LoginRequiredMixin, 
		HasSocialProfileMixin, 
		IncrementViewCountMixin, 
		DetailView
	):
	"""This view permits a user who has a social profile to view another user's social profile."""

	# User's username will be used, hence use the User model
	model = SocialProfile
	slug_url_kwarg = "username"
	slug_field = "username"
	template_name = 'socialize/socialprofile_detail.html'

	def get_object(self):
		# directly return social profile since thanks to our mixin, 
		# we are sure user has social profile
		return self.request.user.social_profile

	def get(self, request, *args, **kwargs):
		self.set_view_count()
		return super().get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		profile = self.object
		social_media = profile.social_media

		context['profile_user'] = profile.user
		context['profile_info'] = {
			_('Level'): profile.get_level_display(),
			_('Speciality'): profile.speciality,
			_('School'): profile.school.name if profile.school_id else _('Not provided'),
			_('Gender'): profile.gender,
			_('Aged between'): profile.age_range,
			_('A little about me'): about_me if (about_me := profile.about_me) else _('Not provided'),
			_('My hobbies and interests'): hobbies if (hobbies := profile.hobbies) else _('Not provided'),
			_('Currently'): profile.get_current_relationship_display(),
			_('Interested in'): profile.get_interested_relationship_display(),
		}
		context['social_media_links'] = {
			_('Email'): email if (email := social_media.email) else '',
			'GitHub': github if (github := social_media.github_follow) else '',
			_('Website'): web_links if (web_links := social_media.website_follow) else '',
			'Tiktok': tiktok if (tiktok := social_media.tiktok_follow) else '',
			'Facebook': facebook if (facebook := social_media.facebook_follow) else '',
			'Twitter': twitter if (twitter := social_media.twitter_follow) else '',
			'Instagram': instagram if (instagram := social_media.instagram_follow) else ''
		}
		
		return context


class CamerSchoolsProfileView(TemplateView):
	template_name = 'socialize/camerschools_profile.html'


@user_passes_test(
	has_social_profile, 
	# link to go to if user does not pass test.
	login_url=reverse_lazy('socialize:create-profile')
)
@login_required
@require_GET
def friend_finder(request):
	# use empty queryset since we won't be displaying any results on this template.
	filter = SocialProfileFilter(request.GET, queryset=SocialProfile.objects.none())

	context = {
		'filter': filter,
		'random_profiles': get_random_profiles()
	}

	return render(request, 'socialize/socialprofile_filter.html', context)


class SocialProfileList(LoginRequiredMixin, HasSocialProfileMixin, FilterView):
	## List of filtered social profile results
	# by default, this will return all the objects of the model.
	model = SocialProfile
	# context_object_name = 'social_profiles'
	filterset_class = SocialProfileFilter
	template_name = 'socialize/socialprofile_list.html'
	template_name_suffix = '_list'
	paginate_by = 7

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['random_profiles'] = get_random_profiles()

		return context


## Bookmarking
@user_passes_test(
	has_social_profile, 
	login_url=reverse_lazy('socialize:create-profile')
)
@login_required
@require_POST
def social_profile_bookmark_toggle(request):
	"""This view handles bookmarking for past papers"""
	user, POST = request.user, request.POST
	id, action = POST.get('id'), POST.get('action')
	# remember SocialProfile has no attribute id.
	social_profile = get_object_or_404(SocialProfile, user_id=id)

	# user can't bookmark his own profile
	# remember there is a test to ensure only users with social profiles can access this view
	if user.social_profile == social_profile:
		return JsonResponse({'bookmarked': False}, status=403) #Forbidden

	# if vote is new (not removing bookmark)
	if action == 'bookmark':
		social_profile.bookmarkers.add(user)
		return JsonResponse({'bookmarked': True}, status=200)

	# if user is retracting bookmark
	elif action == 'recall-bookmark':
		social_profile.bookmarkers.remove(user)
		return JsonResponse({'unbookmarked': True}, status=200)
	else:
		return JsonResponse({'error': _('Invalid action')}, status=400)


