import django_filters as filters
from django_filters.views import FilterView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import F, Q
from django.db.models.query import Prefetch
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.translation import get_language, gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from functools import reduce

from core.constants import (
	REQUIRED_DOWNVOTE_POINTS, ASK_QUESTION_POINTS_CHANGE,
)
from core.mixins import GetObjectMixin, IncrementViewCountMixin
from core.models import Institution
from core.utils import should_redirect, translate_text
from notifications.models import Notification
from notifications.signals import notify
from ..forms import AcademicQuestionForm, DiscussQuestionForm
from ..mixins import (
	CanEditQuestionMixin, CanDeleteQuestionMixin,
)
from ..models import (
	Subject, AcademicQuestion, DiscussQuestion, 
	TaggedAcademicQuestion, TaggedDiscussQuestion, 
)

User = get_user_model()


class QuestionsExplain(TemplateView):
	template_name = "qa_site/questions_explain.html"


class AcademicQuestionCreate(LoginRequiredMixin, CreateView):
	form_class = AcademicQuestionForm
	model = AcademicQuestion

	def form_valid(self, form):
		question = self.object = form.save(commit=False)
		poster = self.request.user
		current_lang = get_language()

		## TRANSLATION (successfully translate before saving any object.)
		if settings.ENABLE_GOOGLE_TRANSLATE:
			# get language to translate to
			trans_lang = 'fr' if current_lang == 'en' else 'en'

			translatable_fields = ['title', 'content', ]
			translate_fields = [field + '_' + trans_lang for field in translatable_fields]
			
			# fields that need to be translated. (see translation.py)
			# ommit slug because google corrects the slug to appropriate string b4 translating.
			# see demo in google translate .
			field_values = [getattr(question, field) for field in translatable_fields]
			trans_results = translate_text(field_values, trans_lang)
			
			# each dict in trans_results contains keys: 
			# `input`, `translatedText`, `detectedSourceLanguage`
			for trans_field, result_dict in zip(translate_fields, trans_results):
				setattr(question, trans_field, result_dict['translatedText'])

			# if object was saved in say english, slug_en will be set but not slug_fr. 
			# so get the slug in the other language
			# also, at this point, these attributes will be set(translated)
			if trans_lang == 'fr':
				question.slug_fr = slugify(question.title_fr)
			elif trans_lang == 'en':
				question.slug_en = slugify(question.title_en)

		with transaction.atomic():
			poster.site_points = F('site_points') + ASK_QUESTION_POINTS_CHANGE
			poster.save(update_fields=['site_points'])
			
			question.poster = poster
			question.original_language = current_lang
			question.save()	

			# save m2m fields(such as tags, upvoters, ..) since we used commit=False
			form.save_m2m()

		return redirect(question)


class AcademicQuestionDetail(GetObjectMixin, IncrementViewCountMixin, DetailView):
	model = AcademicQuestion
	context_object_name = 'question'

	def get(self, request, *args, **kwargs):
		if should_redirect(object := self.get_object(), kwargs.get('slug')):
			return redirect(object, permanent=True)
		
		self.set_view_count()
		return super().get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		NUM_RELATED_QSTNS = 4
		context = super().get_context_data(**kwargs)
		question, user, all_users = self.object, self.request.user, User.objects.active()

		## RELATED QUESTIONS
		related_items = TaggedAcademicQuestion.objects.none()
		question_tags = question.tags.all()
		for tag in question_tags:
			# build queryset of all TaggedItems. 
			# since our TaggedAcademicQuestion serves as the through model, 
			# it contains each tag and the object(question) it's linked to
			# so get union(|) of these querysets
			related_items |= tag.academic_questions.exclude(content_object=question)

		# grab each question's id for filtering
		related_items_ids = related_items.values_list('content_object_id', flat=True)
		related_qstns = AcademicQuestion.objects.filter(
			id__in=related_items_ids
		).only('title') \
		.prefetch_related(
			Prefetch('upvoters', queryset=all_users.only('id')),
			Prefetch('downvoters', queryset=all_users.only('id'))
		) \
		.order_by('-posted_datetime')[:NUM_RELATED_QSTNS]
		
		context['question_tags'] = question_tags
		context['num_comments'] = question.comments.count()
		context['related_qstns'] = related_qstns
		context['is_following'] = user in question.followers.only('id')
		context['required_downvote_points'] = REQUIRED_DOWNVOTE_POINTS
		context['no_slug_url'] = question.get_absolute_url(with_slug=False)
		context['can_edit_question'] = False if user.is_anonymous else user.can_edit_question(question)
		context['can_delete_question'] = False if user.is_anonymous else user.can_delete_question(question)
		context['unfollow_text'] = _('to unfollow this question (stop getting notifications when anyone posts a new answer to this question).')
		context['follow_text'] = _('to follow this question (get notifications when anyone posts a new answer to this question).')
		return context


class AcademicQuestionDelete(GetObjectMixin, CanDeleteQuestionMixin, DeleteView):
	model = AcademicQuestion
	success_url = reverse_lazy('qa_site:academic-question-list')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['ask_question_points_change'] = ASK_QUESTION_POINTS_CHANGE
		return context

	def delete(self, request, *args, **kwargs):
		# recall that when user asks a question, he is given some points.
		# remove those points now since he is deleting the question
		# he should be told in frontend
		question = self.get_object()

		# don't use request.user 
		# since moderator or staff could be the ones calling this view.
		# rather use question.poster
		poster = question.poster
		poster.site_points = F('site_points') - ASK_QUESTION_POINTS_CHANGE
		poster.save(update_fields=['site_points'])

		question.delete()
		return redirect(self.get_success_url())


class AcademicQuestionUpdate(GetObjectMixin, CanEditQuestionMixin, UpdateView):
	model = AcademicQuestion
	form_class = AcademicQuestionForm
	template_name = 'qa_site/academicquestion_update.html'

	def form_valid(self, form):
		question = form.save(commit=False)
		current_lang = get_language()
		changed_data = form.changed_data

		## TRANSLATION
		if settings.ENABLE_GOOGLE_TRANSLATE:
			# get fields that are translatable(permitted to be translated)
			permitted_fields = ['title', 'content', ]

			updated_fields = [
				field for field in changed_data if \
				not field.endswith('_en') and not field.endswith('_fr')
			]
			desired_fields = [field for field in updated_fields if field in permitted_fields]

			trans_lang = 'fr' if current_lang == 'en' else 'en'

			# get and translated values that need to be translated
			field_values = [getattr(question, field) for field in desired_fields]
			
			if field_values:
				trans_results = translate_text(field_values, trans_lang)
				
				# get fields that need to be set after translation
				translate_fields = [field + '_' + trans_lang for field in desired_fields]

				# each dict in trans_results contains keys: 
				# `input`, `translatedText`, `detectedSourceLanguage`
				for trans_field, result_dict in zip(translate_fields, trans_results):
					setattr(question, trans_field, result_dict['translatedText'])

		with transaction.atomic():
			question.update_language = current_lang
			question.save()

			if 'tags' in changed_data:
				question.tags.set(form.cleaned_data['tags'], clear=True)

		# notify users that are following this question
		for follower in question.followers.all():
			notify.send(
				sender=follower,  # just use follower as sender,
				recipient=follower, 
				verb=_('There was an activity on the question'),
				target=question,
				category=Notification.FOLLOWING
			)

		return redirect(question)


class AcademicQuestionFilter(filters.FilterSet):
	title = filters.CharFilter(label=_('Keywords'), method='filter_title')
	tags = filters.CharFilter(
		label=_('Tags'), 
		method='filter_tags', 
		help_text='Space separated tags. eg. tag1 tag2'
	)

	class Meta:
		model = AcademicQuestion
		fields = ['subject', 'title', 'tags', ]
	
	def __init__(self, *args, **kwargs):
		# set label for fields,
		# this is to enable translation of labels.
		super().__init__(*args, **kwargs)
		self.filters['subject'].label = _('Subject')

	def filter_title(self, queryset, name, value):
		# prins False; that means leading and trailing whitespace is stripped.
		# cool
		# print(value.endswith(' '))

		value_list = value.split()
		qs = queryset.filter(
			reduce(
				lambda x, y: x | y, 
				[Q(title__icontains=word) for word in value_list]
			)
		)
		return qs

	def filter_tags(self, queryset, name, value):
		tag_list = value.split()
		qs = queryset.filter(
			reduce(
				lambda x, y: x | y, 
				[Q(tags__name__icontains=word) for word in tag_list]
			)
		)
		return qs


class AcademicQuestionList(FilterView):
	model = AcademicQuestion
	# context_object_name = 'questions'
	filterset_class = AcademicQuestionFilter
	template_name = 'qa_site/academicquestion_list.html'
	template_name_suffix = '_list'
	paginate_by = 7

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		subjects = Subject.objects.prefetch_related(
			Prefetch('academic_questions', queryset=AcademicQuestion.objects.only('id'))
		)
		context['subjects'] = subjects
		context['total_num_qstns'] = AcademicQuestion.objects.count()

		# optimise queries by using prefetch related on objects for the current page
		page_obj = context.get('page_obj')
		paginator = page_obj.paginator

		page_num = self.request.GET.get('page', 1)
		page_content = paginator.page(page_num).object_list
		# prefetch upvoters & downvoters so as to fasten calculation of score.
		# django will get only the ids of upvoters & downvoters since in frontent(template), 
		# we just need the number of upvoters & downvoters to get the score of a question
		page_content.prefetch_related('tags', 'upvoters', 'downvoters')

		context['page_content'] = page_content

		# NOTE: don't modify page_obj since 
		# the context variable `is_paginated` depends on its content.
		return context


class DiscussQuestionCreate(LoginRequiredMixin, CreateView):
	form_class = DiscussQuestionForm
	model = DiscussQuestionForm
	template_name = 'qa_site/discussquestion_form.html'

	def form_valid(self, form):
		question = self.object = form.save(commit=False)
		poster, current_lang = self.request.user, get_language()

		## TRANSLATION
		if settings.ENABLE_GOOGLE_TRANSLATE:
			# get language to translate to
			trans_lang = 'fr' if current_lang == 'en' else 'en'

			translatable_fields = ['content', ]
			translate_fields = [field + '_' + trans_lang for field in translatable_fields]
			
			# fields that need to be translated. (see translation.py)
			# ommit slug because google corrects the slug to appropriate string b4 translating.
			# see demo in google translate .
			field_values = [getattr(question, field) for field in translatable_fields]
			trans_results = translate_text(field_values, trans_lang)
			
			# each dict in trans_results contains keys: 
			# `input`, `translatedText`, `detectedSourceLanguage`
			for trans_field, result_dict in zip(translate_fields, trans_results):
				setattr(question, trans_field, result_dict['translatedText'])

		with transaction.atomic():
			poster.site_points = F('site_points') + ASK_QUESTION_POINTS_CHANGE
			poster.save(update_fields=['site_points'])

			question.school = form.cleaned_data['school']
			question.poster = poster
			question.original_language = current_lang
			question.save()	
			form.save_m2m()

		return redirect(question)


class DiscussQuestionDelete(GetObjectMixin, CanDeleteQuestionMixin, DeleteView):
	model = DiscussQuestion
	success_url = reverse_lazy('qa_site:discuss-question-list')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['ask_question_points_change'] = ASK_QUESTION_POINTS_CHANGE
		return context

	def delete(self, request, *args, **kwargs):
		# recall that when user asks a question, he is given some points.
		# remove those points now since he is deleting the question
		# he should be told in frontend
		
		question = self.get_object()
		# don't use request.user 
		# since moderator or staff could be the ones calling this view.
		# rather use question.poster
		poster = question.poster
		poster.site_points = F('site_points') - ASK_QUESTION_POINTS_CHANGE
		poster.save(update_fields=['site_points'])

		question.delete()
		return redirect(self.get_success_url())


class DiscussQuestionUpdate(GetObjectMixin, CanEditQuestionMixin, UpdateView):
	model = DiscussQuestion
	form_class = DiscussQuestionForm
	template_name = 'qa_site/discussquestion_update.html'

	def form_valid(self, form):
		question = form.save(commit=False)
		current_lang = get_language()
		changed_data = form.changed_data

		## TRANSLATION
		if settings.ENABLE_GOOGLE_TRANSLATE:
			# get fields that are translatable(permitted to be translated)
			permitted_fields = ['content', ]

			updated_fields = [
				field for field in changed_data if \
				not field.endswith('_en') and not field.endswith('_fr')
			]
			desired_fields = [field for field in updated_fields if field in permitted_fields]

			trans_lang = 'fr' if current_lang == 'en' else 'en'

			# get and translated values that need to be translated
			field_values = [getattr(question, field) for field in desired_fields]
		
			if field_values:
				trans_results = translate_text(field_values, trans_lang)
				
				# get fields that need to be set after translation
				translate_fields = [field + '_' + trans_lang for field in desired_fields]

				# each dict in trans_results contains keys: 
				# `input`, `translatedText`, `detectedSourceLanguage`
				for trans_field, result_dict in zip(translate_fields, trans_results):
					setattr(question, trans_field, result_dict['translatedText'])

		with transaction.atomic():
			question.update_language = current_lang
			question.save()

			if 'tags' in changed_data:
				question.tags.set(form.cleaned_data['tags'], clear=True)

		# notify users that are following this question
		for follower in question.followers.all():
			notify.send(
				sender=follower,  # just use follower as sender,
				recipient=follower, 
				verb=_('There was an activity on the question'),
				target=question,
				category=Notification.FOLLOWING
			)

		return redirect(question)


class DiscussQuestionFilter(filters.FilterSet):
	# this query will take long in cases where the school question is too long
	# which will occur occasionally 
	# TODO use postgres text search 
	content = filters.CharFilter(label=_('Keywords'), method='filter_content')
	tags = filters.CharFilter(
		label=_('Tags'), 
		method='filter_tags',
		help_text='Space separated tags. eg. tag1 tag2'
	)

	class Meta:
		model = DiscussQuestion
		fields = ['school', 'content', 'tags', ]
	
	def __init__(self, *args, **kwargs):
		# set label for fields,
		# this is to enable translation of labels.
		super().__init__(*args, **kwargs)
		self.filters['school'].label = _('School')

	def filter_content(self, queryset, name, value):
		value_list = value.split()
		qs = queryset.filter(
			reduce(
				lambda x, y: x | y, 
				[Q(content__icontains=word) for word in value_list]
			)
		)
		return qs

	def filter_tags(self, queryset, name, value):
		tag_list = value.split()
		qs = queryset.filter(
			reduce(
				lambda x, y: x | y, 
				[Q(tags__name__icontains=word) for word in tag_list]
			)
		)
		return qs


class DiscussQuestionList(FilterView):
	model = DiscussQuestion
	# context_object_name = 'questions'
	filterset_class = DiscussQuestionFilter
	template_name = 'qa_site/discussquestion_list.html'
	template_name_suffix = '_list'
	paginate_by = 7

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		schools = Institution.objects.prefetch_related(
			Prefetch('questions', queryset=DiscussQuestion.objects.only('id'))
		)
		context['schools'] = schools
		context['total_num_qstns'] = DiscussQuestion.objects.count()

		# optimise queries by using prefetch related on objects for the current page
		page_obj = context.get('page_obj')
		paginator = page_obj.paginator

		page_num = self.request.GET.get('page', 1)
		page_content = paginator.page(page_num).object_list
		page_content.prefetch_related('upvoters', 'downvoters')
		context['page_content'] = page_content

		# print('page content', page_content)
		# print('page obj', page_obj)
		
		return context


class DiscussQuestionDetail(GetObjectMixin, IncrementViewCountMixin, DetailView):
	model = DiscussQuestion
	context_object_name = 'question'

	def get(self, request, *args, **kwargs):
		self.set_view_count()
		return super().get(request, *args, **kwargs)
		
	def get_context_data(self, **kwargs):
		NUM_RELATED_QSTNS = 4
		context = super().get_context_data(**kwargs)
		question, user, all_users = self.object, self.request.user, User.objects.active()

		## RELATED QUESTIONS
		related_items = TaggedDiscussQuestion.objects.none()
		question_tags = question.tags.all()
		for tag in question_tags:
			# build queryset of all TaggedItems. 
			# since our TaggedDiscussQuestion serves as the through model, 
			# it contains each tag and the object(question) it's linked to
			# so get union(|) of these querysets
			related_items |= tag.discuss_questions.exclude(content_object=question)

		# grab each question's id for filtering
		related_items_ids = related_items.values_list('content_object_id', flat=True)
		related_qstns = DiscussQuestion.objects.filter(
			id__in=related_items_ids
		).only('content') \
		.prefetch_related(
			Prefetch('upvoters', queryset=all_users.only('id')),
			Prefetch('downvoters', queryset=all_users.only('id'))
		) \
		.order_by('-posted_datetime')[:NUM_RELATED_QSTNS]
		
		context['question_tags'] = question_tags
		context['related_qstns'] = related_qstns
		context['num_comments'] = question.comments.count()
		context['is_following'] = user in question.followers.only('id')
		context['required_downvote_points'] = REQUIRED_DOWNVOTE_POINTS
		context['can_edit_question'] = False if user.is_anonymous else user.can_edit_question(question)
		context['can_delete_question'] = False if user.is_anonymous else user.can_delete_question(question)
		context['unfollow_text'] = _('to unfollow this question (stop getting notifications when anyone posts a new answer to this question).')
		context['follow_text'] = _('to follow this question (get notifications when anyone posts a new answer to this question).')
		return context


