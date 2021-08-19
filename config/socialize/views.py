from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View 
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from .forms import SocialProfileForm, SocialMediaFollowForm
from .models import SocialProfile, SocialMediaFollow


class SocialProfileCreate(View):
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

	
