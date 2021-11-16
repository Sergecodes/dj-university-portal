import django_filters as filters
from django_filters.views import FilterView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import F, Q
from django.db.models.query import Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
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
from .forms import (
	AcademicQuestionForm, SchoolQuestionForm, AcademicAnswerForm,
	AcademicQuestionCommentForm, AcademicAnswerCommentForm,
	SchoolQuestionCommentForm, SchoolAnswerCommentForm, SchoolAnswerForm
)
from notifications.models import Notification
from notifications.signals import notify
from .mixins import (
	CanEditQuestionMixin, CanDeleteQuestionMixin,
	CanEditAnswerMixin, CanDeleteAnswerMixin,
	CanEditCommentMixin, CanDeleteCommentMixin
)
from .models import (
	SchoolAnswer, SchoolQuestionComment, Subject, 
	AcademicQuestion, SchoolQuestion, SchoolAnswerComment,
	AcademicQuestionComment, AcademicAnswerComment,
	TaggedAcademicQuestion, AcademicAnswer, 
)

User = get_user_model()


class QuestionsExplain(TemplateView):
	template_name = "qa_site/questions_explain.html"


class AcademicQuestionCreate(LoginRequiredMixin, CreateView):
	form_class = AcademicQuestionForm
	model = AcademicQuestion

	def form_valid(self, form):
		self.object = form.save(commit=False)
		question, poster = self.object, self.request.user
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

		poster.site_points = F('site_points') + ASK_QUESTION_POINTS_CHANGE
		poster.save(update_fields=['site_points'])
		
		question.poster = poster
		question.original_language = current_lang
		question.save()	
		# save m2m fields(such as tags, upvoters, ..) since we used commit=False
		form.save_m2m()

		return redirect(question)


@method_decorator(login_required, name='post')
class AcademicQuestionDetail(GetObjectMixin, IncrementViewCountMixin, DetailView):
	model = AcademicQuestion
	context_object_name = 'question'

	def post(self, request, *args, **kwargs):
		"""Handle submission of forms such as comments and answers."""
		POST, user = request.POST, request.user
		question = get_object_or_404(AcademicQuestion, id=POST.get('question_id'))

		# if question comment form was submitted
		if 'add_question_comment' in POST:
			comment_form = AcademicQuestionCommentForm(POST)
			# remember if form isn't valid form will be populated with errors..
			# can use `return self.form_invalid(form)` to rerender and populate form with errs.
			if comment_form.is_valid():
				comment = comment_form.save(commit=False)
				user.add_question_comment(question, comment)

		elif 'add_answer_comment' in POST:
			comment_form = AcademicAnswerCommentForm(POST)
			if comment_form.is_valid():
				comment = comment_form.save(commit=False)
				answer = get_object_or_404(AcademicAnswer, id=POST.get('answer_id'))
				user.add_answer_comment(answer, comment)

		elif 'add_answer' in POST:
			answer_form = AcademicAnswerForm(POST)
			if answer_form.is_valid():
				answer = answer_form.save(commit=False)
				added_result = user.add_answer(question, answer, 'academic')

				# if answer wasn't added 
				# (if user has attained number of answers limit)
				if not added_result[0]:
					raise PermissionDenied(added_result[1])

		# redirect to get request. (SEE Post/Redirect/Get)
		# instead of simply returning to get (return get(self,...))
		return redirect(question)
	
	def get(self, request, *args, **kwargs):
		if should_redirect(object := self.get_object(), kwargs.get('slug')):
			return redirect(object, permanent=True)
		
		self.set_view_count()
		return super().get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		NUM_RELATED_QSTNS = 4
		context = super().get_context_data(**kwargs)
		question, user, all_users = self.object, self.request.user, User.objects.active()

		# initialize comment and answer forms
		qstn_comment_form = AcademicQuestionCommentForm()
		answer_form = AcademicAnswerForm()
		ans_comment_form = AcademicAnswerCommentForm()

		context['qstn_comment_form'] = qstn_comment_form
		context['ans_comment_form'] = ans_comment_form
		context['answer_form'] = answer_form
		
		answers = question.answers.prefetch_related(
			'comments', 
			Prefetch('upvoters', queryset=all_users.only('id'))
		).all()
		comments = question.comments.prefetch_related(
			Prefetch('upvoters', queryset=all_users.only('id'))
		).all()


		## RELATED QUESTIONS
		related_items = TaggedAcademicQuestion.objects.none()
		question_tags = question.tags.all()
		for tag in question_tags:
			# build queryset of all TaggedItems. 
			# since our AcademicQuestionTag serves as the through model, 
			# it contains each tag and the object(question) it's linked to
			# so get union(|) of these querysets
			related_items |= tag.academic_questions.exclude(content_object=question)

		# grab each question's id for filtering
		related_items_ids = related_items.values_list('content_object_id', flat=True)
		related_qstns = AcademicQuestion.objects.filter(
			id__in=related_items_ids
		).only('title') \
		.prefetch_related(
			Prefetch('answers', queryset=AcademicAnswer.objects.defer('content')),
			Prefetch('upvoters', queryset=all_users.only('id')),
			Prefetch('downvoters', queryset=all_users.only('id'))
		) \
		.order_by('-posted_datetime')[:NUM_RELATED_QSTNS]
		
		context['question_tags'] = question_tags
		context['answers'] = answers
		context['comments'] = comments
		context['num_answers'] = answers.count()
		context['related_qstns'] = related_qstns
		context['is_following'] = user in question.followers.only('id')
		context['required_downvote_points'] = REQUIRED_DOWNVOTE_POINTS
		context['no_slug_url'] = question.get_absolute_url(with_slug=False)
		context['can_edit_question'] = False if user.is_anonymous else user.can_edit_question(question)
		context['can_delete_question'] = False if user.is_anonymous else user.can_delete_question(question)
		
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
		followers = question.followers.all()
		current_lang = get_language()

		## TRANSLATION
		if settings.ENABLE_GOOGLE_TRANSLATE:
			changed_data = form.changed_data

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

		question.update_language = current_lang
		question.save()

		if 'tags' in changed_data:
			question.tags.set(*form.cleaned_data['tags'])
		# print(question.tags.all())

		# notify users that are following this question
		for follower in followers:
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
	tags = filters.CharFilter(label=_('Tags'), method='filter_tags')

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


class SchoolQuestionCreate(LoginRequiredMixin, CreateView):
	form_class = SchoolQuestionForm
	model = SchoolQuestionForm
	template_name = 'qa_site/schoolquestion_form.html'

	def form_valid(self, form):
		self.object = form.save(commit=False)
		school_question, poster = self.object, self.request.user
		school_question.school = form.cleaned_data['school']
		current_lang = get_language()

		## TRANSLATION
		if settings.ENABLE_GOOGLE_TRANSLATE:
			# get language to translate to
			trans_lang = 'fr' if current_lang == 'en' else 'en'

			translatable_fields = ['content', ]
			translate_fields = [field + '_' + trans_lang for field in translatable_fields]
			
			# fields that need to be translated. (see translation.py)
			# ommit slug because google corrects the slug to appropriate string b4 translating.
			# see demo in google translate .
			field_values = [getattr(school_question, field) for field in translatable_fields]
			trans_results = translate_text(field_values, trans_lang)
			
			# each dict in trans_results contains keys: 
			# `input`, `translatedText`, `detectedSourceLanguage`
			for trans_field, result_dict in zip(translate_fields, trans_results):
				setattr(school_question, trans_field, result_dict['translatedText'])

		poster.site_points = F('site_points') + ASK_QUESTION_POINTS_CHANGE
		poster.save(update_fields=['site_points'])

		school_question.poster = poster
		school_question.original_language = get_language()
		school_question.save()	
		form.save_m2m()

		return redirect(school_question)


class SchoolQuestionDelete(GetObjectMixin, CanDeleteQuestionMixin, DeleteView):
	model = SchoolQuestion
	success_url = reverse_lazy('qa_site:school-question-list')

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


class SchoolQuestionUpdate(GetObjectMixin, CanEditQuestionMixin, UpdateView):
	model = SchoolQuestion
	form_class = SchoolQuestionForm
	template_name = 'qa_site/schoolquestion_update.html'

	def form_valid(self, form):
		school_question = form.save(commit=False)
		followers = school_question.followers.all()
		current_lang = get_language()

		## TRANSLATION
		if settings.ENABLE_GOOGLE_TRANSLATE:
			changed_data = form.changed_data

			# get fields that are translatable(permitted to be translated)
			permitted_fields = ['content', ]

			updated_fields = [
				field for field in changed_data if \
				not field.endswith('_en') and not field.endswith('_fr')
			]
			desired_fields = [field for field in updated_fields if field in permitted_fields]

			trans_lang = 'fr' if current_lang == 'en' else 'en'

			# get and translated values that need to be translated
			field_values = [getattr(school_question, field) for field in desired_fields]
		
			if field_values:
				trans_results = translate_text(field_values, trans_lang)
				
				# get fields that need to be set after translation
				translate_fields = [field + '_' + trans_lang for field in desired_fields]

				# each dict in trans_results contains keys: 
				# `input`, `translatedText`, `detectedSourceLanguage`
				for trans_field, result_dict in zip(translate_fields, trans_results):
					setattr(school_question, trans_field, result_dict['translatedText'])

		school_question.update_language = current_lang
		school_question.save()

		# notify users that are following this question
		for follower in followers:
			notify.send(
				sender=follower,  # just use follower as sender,
				recipient=follower, 
				verb=_('There was an activity on the question'),
				target=school_question,
				category=Notification.FOLLOWING
			)

		return redirect(school_question)


class SchoolQuestionFilter(filters.FilterSet):
	# this query will take long in cases where the school question is too long
	# which will occur occasionally 
	# TODO use postgres text search 
	content = filters.CharFilter(label=_('Keywords'), method='filter_content')

	class Meta:
		model = SchoolQuestion
		fields = ['school', 'content',]
	
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


class SchoolQuestionList(FilterView):
	model = SchoolQuestion
	# context_object_name = 'questions'
	filterset_class = SchoolQuestionFilter
	template_name = 'qa_site/schoolquestion_list.html'
	template_name_suffix = '_list'
	paginate_by = 7

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		schools = Institution.objects.prefetch_related(
			Prefetch('questions', queryset=SchoolQuestion.objects.only('id'))
		)
		context['schools'] = schools
		context['total_num_qstns'] = SchoolQuestion.objects.count()

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


@method_decorator(login_required, name='post')
class SchoolQuestionDetail(GetObjectMixin, IncrementViewCountMixin, DetailView):
	model = SchoolQuestion
	context_object_name = 'question'

	def post(self, request, *args, **kwargs):
		"""Handle submission of forms such as comments and answers."""
		POST, user = request.POST, request.user
		question = get_object_or_404(SchoolQuestion, id=POST.get('question_id'))

		# if question comment form was submitted
		if 'add_question_comment' in POST:
			comment_form = SchoolQuestionCommentForm(POST)
			# remember if form isn't valid form will be populated with errors..
			# can use `return self.form_invalid(form)` to rerender and populate form with errs.
			if comment_form.is_valid():
				comment = comment_form.save(commit=False)
				user.add_question_comment(question, comment)

		elif 'add_answer_comment' in POST:
			comment_form = SchoolAnswerCommentForm(POST)
			if comment_form.is_valid():
				comment = comment_form.save(commit=False)
				answer = get_object_or_404(SchoolAnswer, id=POST.get('answer_id'))
				user.add_answer_comment(answer, comment)

		elif 'add_answer' in POST:
			answer_form = SchoolAnswerForm(POST)
			if answer_form.is_valid():
				answer = answer_form.save(commit=False)
				added_result = user.add_answer(question, answer, 'school-based')

				# if answer wasn't added 
				# (if user has attained number of answers limit)
				if not added_result[0]:
					raise PermissionDenied(added_result[1])

		return redirect(question)

	def get(self, request, *args, **kwargs):
		self.set_view_count()
		return super().get(request, *args, **kwargs)
		
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		question, user = self.object, self.request.user

		# initialize comment and answer forms
		qstn_comment_form = SchoolQuestionCommentForm()
		ans_comment_form = SchoolAnswerCommentForm()
		answer_form = SchoolAnswerForm()
		context['qstn_comment_form'] = qstn_comment_form
		context['ans_comment_form'] = ans_comment_form
		context['answer_form'] = answer_form
		
		answers = question.answers.prefetch_related(
			'comments', 
			Prefetch('upvoters', queryset=User.objects.active().only('id'))
		).all()
		comments = question.comments.prefetch_related(
			Prefetch('upvoters', queryset=User.objects.active().only('id'))
		).all()

		context['answers'] = answers
		context['comments'] = comments
		context['num_answers'] = answers.count()
		context['is_following'] = user in question.followers.only('id')
		context['required_downvote_points'] = REQUIRED_DOWNVOTE_POINTS
		context['can_edit_question'] = False if user.is_anonymous else user.can_edit_question(question)
		context['can_delete_question'] = False if user.is_anonymous else user.can_delete_question(question)

		return context


## EDIT AND DELETE ANSWER AND COMMENT ##

## COMMENT UPDATE AND DELETE
# due to the CanEditCommentMixin, this class needs to be used only with comments
class CommentUpdate(GetObjectMixin, CanEditCommentMixin, UpdateView):
	# set fields to update.
	# if you use the form_class attribute instead, 
	# you will manually need to save/update some fields
	fields = ['content']
	template_name = 'qa_site/misc/comment_edit.html'

	def get_success_url(self):
		return self.get_object().parent_object.get_absolute_url()

	def form_valid(self, form):
		# if comment was modified, save it.
		# print(form.changed_data)
		if 'content' in form.changed_data:
			comment = form.save(commit=False)
			comment.update_language = get_language()
			comment.save()

		return redirect(self.get_success_url())


class AcademicQuestionCommentUpdate(CommentUpdate):
	model = AcademicQuestionComment

class AcademicAnswerCommentUpdate(CommentUpdate):
	model = AcademicAnswerComment

class SchoolQuestionCommentUpdate(CommentUpdate):
	model = SchoolQuestionComment

class SchoolAnswerCommentUpdate(CommentUpdate):
	model = SchoolAnswerComment


class CommentDelete(GetObjectMixin, CanDeleteCommentMixin, DeleteView):
	template_name = 'qa_site/misc/comment_confirm_delete.html'

	def get_success_url(self):
		return self.get_object().parent_object.get_absolute_url()


class AcademicQuestionCommentDelete(CommentDelete):
	model = AcademicQuestionComment

class AcademicAnswerCommentDelete(CommentDelete):
	model = AcademicAnswerComment

class SchoolQuestionCommentDelete(CommentDelete):
	model = SchoolQuestionComment

class SchoolAnswerCommentDelete(CommentDelete):
	model = SchoolAnswerComment


## ANSWER UPDATE AND DELETE
class AnswerUpdate(GetObjectMixin, CanEditAnswerMixin, UpdateView):
	# set fields to update.
	# if you use the form_class attribute instead, 
	# you will manually need to save/update some fields
	fields = ['content']
	template_name = 'qa_site/misc/answer_edit.html'

	def form_valid(self, form):
		answer = form.save(commit=False)
		question = answer.question

		if 'content' in form.changed_data:
			current_lang = get_language()

			## TRANSLATION
			if settings.ENABLE_GOOGLE_TRANSLATE:
				# get language to translate to
				trans_lang = 'fr' if current_lang == 'en' else 'en'
				translated_content = translate_text(answer.content, trans_lang)['translatedText']
				setattr(answer, f'content_{trans_lang}', translated_content)

			answer.update_language = current_lang
			answer.save()

			# notify users that are following this answer's question
			for follower in question.followers.all():
				notify.send(
					sender=follower,  # just use follower as sender,
					recipient=follower, 
					verb=_('There was an activity on the question'),
					target=question,
					category=Notification.FOLLOWING
				)
		
		return redirect(question)


class AcademicAnswerUpdate(AnswerUpdate):
	model = AcademicAnswer

class SchoolAnswerUpdate(AnswerUpdate):
	model = SchoolAnswer


class AnswerDelete(GetObjectMixin, CanDeleteAnswerMixin, DeleteView):
	template_name = 'qa_site/misc/answer_confirm_delete.html'
	
	def get_success_url(self):
		# self.question is set in the delete method below
		return self.question.get_absolute_url()

	def delete(self, request, *args, **kwargs):
		self.question = self.get_object().question
		question = self.question

		# notify users that are following this answer's question
		for follower in question.followers.all():
			notify.send(
				sender=follower,  # just use follower as sender,
				recipient=follower, 
				verb=_('There was an activity on the question'),
				target=question,
				category=Notification.FOLLOWING
			)

		# call super method to delete the object etc
		return super().delete(request, *args, **kwargs)


class AcademicAnswerDelete(AnswerDelete):
	model = AcademicAnswer

class SchoolAnswerDelete(AnswerDelete):
	model = SchoolAnswer

