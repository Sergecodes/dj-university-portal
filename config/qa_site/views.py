import django_filters as filters
from django_filters.views import FilterView
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import Prefetch
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from taggit.models import TaggedItem

from .forms import (
	AcademicQuestionForm, SchoolQuestionForm, AcademicAnswerForm,
	AcademicQuestionCommentForm, AcademicAnswerCommentForm,
	SchoolQuestionCommentForm, SchoolAnswerCommentForm, SchoolAnswerForm
)
from .models import (
	Subject, AcademicAnswer, SchoolAnswer,
	AcademicAnswerComment, SchoolAnswerComment,
	AcademicQuestion, SchoolQuestion, SchoolQuestionTag,
	AcademicQuestionComment, SchoolQuestionComment
)

User = get_user_model()


class QuestionsExplain(TemplateView):
	template_name = "qa_site/questions_explain.html"


class AcademicQuestionCreate(LoginRequiredMixin, CreateView):
	form_class = AcademicQuestionForm
	model = AcademicQuestion
	# success_url = '/'
	success_url = reverse_lazy('qa_site:academic-question-detail')

	def form_valid(self, form):
		request = self.request
		self.object = form.save(commit=False)
		question = self.object
		question.poster = request.user
		question.save()	

		return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name='post')
class AcademicQuestionDetail(DetailView):
	model = AcademicQuestion
	context_object_name = 'question'

	def post(self, request, *args, **kwargs):
		"""Handle submission of forms such as comments and answers."""
		POST = request.POST
		question = get_object_or_404(AcademicQuestion, id=POST.get('question_id'))

		# if question comment form was submitted
		if 'add_question_comment' in POST:
			comment_form = AcademicQuestionCommentForm(POST)
			# remember if form isn't valid form will be populated with errors..
			# can use `return self.form_invalid(form)` to rerender and populate form with errs.
			if comment_form.is_valid():
				comment = comment_form.save(commit=False)
				comment.poster = request.user
				comment.question = question
				comment.save()

		elif 'add_answer_comment' in POST:
			comment_form = AcademicAnswerCommentForm(POST)
			if comment_form.is_valid():
				comment = comment_form.save(commit=False)
				comment.poster = request.user
				comment.answer = get_object_or_404(AcademicAnswer, id=POST.get('answer_id'))
				comment.save()

		elif 'add_answer' in POST:
			answer_form = AcademicAnswerForm(POST)
			if answer_form.is_valid():
				answer = answer_form.save(commit=False)
				answer.poster = request.user
				answer.question = question
				answer.save()

		# redirect to get request. (SEE Post/Redirect/Get)
		# do not to return get(self,...)
		return HttpResponseRedirect(question.get_absolute_url())

	def get_context_data(self, **kwargs):
		NUM_RELATED_QSTNS = 4
		context = super().get_context_data(**kwargs)
		question, all_users = self.object, User.objects.all()

		# initialize comment and answer forms
		qstn_comment_form = AcademicQuestionCommentForm()
		ans_comment_form = AcademicAnswerCommentForm()
		answer_form = AcademicAnswerForm()
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

		related_items = TaggedItem.objects.none()
		question_tags = question.tags.all()
		for tag in question_tags:
			# build queryset of all TaggedItems. 
			# a TaggedItem contains each tag and the object it's linked to, so get union(|) of these querysets
			related_items |= tag.taggit_taggeditem_items.exclude(object_id = question.id)

		# TaggedItem doesn't have a direct link to the object, so grap object ids and use them
		ids = related_items.values_list('object_id', flat=True)

		related_qstns = AcademicQuestion.objects.filter(
			id__in=ids
		).only('title') \
		.prefetch_related(
			Prefetch('answers', queryset=AcademicAnswer.objects.all().defer('content')),
			Prefetch('upvoters', queryset=all_users.only('id')),
			Prefetch('downvoters', queryset=all_users.only('id'))
		) \
		.order_by('-posted_datetime')[:NUM_RELATED_QSTNS]
		
		context['question_tags'] = question_tags
		context['answers'] = answers
		context['comments'] = comments
		context['num_answers'] = answers.count()
		context['related_qstns'] = related_qstns
		return context


class AcademicQuestionFilter(filters.FilterSet):
	title = filters.CharFilter(label=_('Keyword'), lookup_expr='icontains')

	class Meta:
		model = AcademicQuestion
		fields = ['subject', 'title', ]

	@property
	def qs(self):
		parent = super().qs
		return parent.order_by('-posted_datetime')


class AcademicQuestionList(FilterView):
	model = AcademicQuestion
	# context_object_name = 'questions'
	filterset_class = AcademicQuestionFilter
	template_name = 'qa_site/academicquestion_list.html'
	template_name_suffix = '_list'
	paginate_by = 2

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		subjects = Subject.objects.all().prefetch_related(
			Prefetch('academic_questions', queryset=AcademicQuestion.objects.all().only('id'))
		)
		num_questions = 0
		for subject in subjects:
			num_questions += subject.academic_questions.count()

		context['subjects'] = Subject.objects.all()
		context['total_num_qstns'] = num_questions

		# optimise queries by using prefetch related on objects for the current page
		page_obj = context.get('page_obj')
		paginator = page_obj.paginator

		page_num = self.request.GET.get('page', 1)
		page_content = paginator.page(page_num).object_list
		# prefetch upvoters & downvoters so as to fasten calculation of score.
		# django will get only the ids of upvoters & downvoters since in frontent(template), we just need the number of upvoters & downvoters to get the score of a question
		page_content.prefetch_related('tags', 'upvoters', 'downvoters')

		context['page_content'] = page_content

		# note: don't modify page_obj since the context variable `is_paginaged` depends on its content.
		return context


class SchoolQuestionCreate(LoginRequiredMixin, CreateView):
	form_class = SchoolQuestionForm
	model = SchoolQuestionForm
	template_name = 'qa_site/schoolquestion_form.html'
	success_url = reverse_lazy('qa_site:school-question-detail')

	def form_valid(self, form):
		request = self.request
		self.object = form.save(commit=False)
		school_question = self.object
		school_question.school = form.cleaned_data['school']
		school_question.poster = request.user
		school_question.save()	

		return HttpResponseRedirect(self.get_success_url())


class SchoolQuestionFilter(filters.FilterSet):
	content = filters.CharFilter(label=_('Keyword'), lookup_expr='icontains')

	class Meta:
		model = SchoolQuestion
		fields = ['school', 'content', 'tags']

	@property
	def qs(self):
		parent = super().qs
		return parent.order_by('-posted_datetime')


class SchoolQuestionList(FilterView):
	model = SchoolQuestion
	# context_object_name = 'questions'
	filterset_class = SchoolQuestionFilter
	template_name = 'qa_site/schoolquestion_list.html'
	template_name_suffix = '_list'
	paginate_by = 2

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		# optimise queries by using prefetch related on objects for the current page
		page_obj = context.get('page_obj')
		paginator = page_obj.paginator

		page_num = self.request.GET.get('page', 1)
		page_content = paginator.page(page_num).object_list
		page_content.prefetch_related('tags', 'upvoters', 'downvoters')
		context['page_content'] = page_content
		
		return context


@method_decorator(login_required, name='post')
class SchoolQuestionDetail(DetailView):
	model = SchoolQuestion
	context_object_name = 'question'

	def post(self, request, *args, **kwargs):
		"""Handle submission of forms such as comments and answers."""
		POST = request.POST
		question = get_object_or_404(SchoolQuestion, id=POST.get('question_id'))

		# if question comment form was submitted
		if 'add_question_comment' in POST:
			comment_form = SchoolQuestionCommentForm(POST)
			# remember if form isn't valid form will be populated with errors..
			# can use `return self.form_invalid(form)` to rerender and populate form with errs.
			if comment_form.is_valid():
				comment = comment_form.save(commit=False)
				comment.poster = request.user
				comment.question = question
				comment.save()

		elif 'add_answer_comment' in POST:
			comment_form = SchoolAnswerCommentForm(POST)
			if comment_form.is_valid():
				comment = comment_form.save(commit=False)
				comment.poster = request.user
				comment.answer = get_object_or_404(AcademicAnswer, id=POST.get('answer_id'))
				comment.save()

		elif 'add_answer' in POST:
			answer_form = SchoolAnswerForm(POST)
			if answer_form.is_valid():
				answer = answer_form.save(commit=False)
				answer.poster = request.user
				answer.question = question
				answer.save()

		return HttpResponseRedirect(question.get_absolute_url())

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		question = self.object

		# initialize comment and answer forms
		qstn_comment_form = SchoolQuestionCommentForm()
		ans_comment_form = SchoolAnswerCommentForm()
		answer_form = SchoolAnswerForm()
		context['qstn_comment_form'] = qstn_comment_form
		context['ans_comment_form'] = ans_comment_form
		context['answer_form'] = answer_form
		
		answers = question.answers.prefetch_related(
			'comments', 
			Prefetch('upvoters', queryset=User.objects.all().only('id'))
		).all()
		comments = question.comments.prefetch_related(
			Prefetch('upvoters', queryset=User.objects.all().only('id'))
		).all()

		context['question_tags'] = question.tags.all()
		context['answers'] = answers
		context['comments'] = comments
		context['num_answers'] = answers.count()

		return context


@login_required
def vote_academic_thread(request):
	"""
	This view handles upvotes and downvotes for questions, answers and comments of an academic question.
	"""
	user, POST = request.user, request.POST
	thread_id, thread_type = int(POST.get('id')), POST.get('thread_type')
	vote_action, vote_type = POST.get('action'), POST.get('vote_type')
	print(POST)
	
	# possible thread types are {question, answer, question-comment, answer-comment}
	if thread_type == 'question':
		object = get_object_or_404(AcademicQuestion, pk=thread_id)
	elif thread_type == 'answer':
		object = get_object_or_404(AcademicAnswer, pk=thread_id)
	elif thread_type == 'question-comment':
		object = get_object_or_404(AcademicQuestionComment, pk=thread_id)
	elif thread_type == 'answer-comment':
		object = get_object_or_404(AcademicAnswerComment, pk=thread_id)
	else:
		raise ValueError("_(Invalid thread type)")

	if thread_type == 'question' or thread_type == 'answer':
		# verify if user has already upvoted and downvoted question or answer
		already_upvoted = user in object.upvoters.all()
		already_downvoted = user in object.downvoters.all()

		# if vote is new (not retracting a previous vote)
		if vote_action == 'vote':
			# if user has no previous vote on the question or answer
			if not already_upvoted and not already_downvoted:
				if vote_type == 'up':
					object.upvoters.add(user)
					return HttpResponse(object.upvote_count)

				elif vote_type == 'down':
					object.downvoters.add(user)	
					return HttpResponse(object.downvote_count)

				else:
					return HttpResponse('Error - Unknown vote type')
			else:
				return HttpResponse('Error - Already voted')

		# if user is retracting a vote
		elif vote_action == 'recall-vote':
			if vote_type == 'up' and already_upvoted:
				object.upvoters.remove(user)
				return HttpResponse(object.upvote_count)

			elif vote_type == 'down' and already_downvoted:
				object.downvoters.remove(user)
				return HttpResponse(object.downvote_count)
			else:
				return HttpResponse('Error - Unknown vote type or no vote to recall')
		else:
			return HttpResponse('Error - bad action')
	
	# only upvotes are supported on comments
	elif thread_type == 'question-comment' or thread_type == 'answer-comment':
		already_upvoted = user in object.upvoters.all()

		if vote_action == 'vote':
			if not already_upvoted:
				if vote_type == 'up':
					object.upvoters.add(user)
					return HttpResponse(object.vote_count)
				else:
					return HttpResponse('Error - Unknown vote type')
			else:
				return HttpResponse('Error - Already voted')

		elif vote_action == 'recall-vote':
			if vote_type == 'up' and already_upvoted:
				object.upvoters.remove(user)
				return HttpResponse(object.vote_count)
			else:
				return HttpResponse('Error - Unknown vote type or no vote to recall')
		else:
			return HttpResponse('Error - bad action')


@login_required
def vote_school_thread(request):
	"""
	This view handles upvotes and downvotes for questions, answers and comments of as school-based question.
	"""
	user, POST = request.user, request.POST
	thread_id, thread_type = int(POST.get('id')), POST.get('thread_type')
	vote_action, vote_type = POST.get('action'), POST.get('vote_type')
	print(POST)

	# possible thread types are {question, answer, question-comment, answer-comment}
	if thread_type == 'question':
		object = get_object_or_404(SchoolQuestion, pk=thread_id)
	elif thread_type == 'answer':
		object = get_object_or_404(SchoolAnswer, pk=thread_id)
	elif thread_type == 'question-comment':
		object = get_object_or_404(SchoolQuestionComment, pk=thread_id)
	elif thread_type == 'answer-comment':
		object = get_object_or_404(SchoolAnswerComment, pk=thread_id)
	else:
		raise ValueError("_(Invalid thread type)")

	if thread_type == 'question' or thread_type == 'answer':
		# verify if user has already upvoted and downvoted question or answer
		already_upvoted = user in object.upvoters.all()
		already_downvoted = user in object.downvoters.all()

		# if vote is new (not retracting a previous vote)
		if vote_action == 'vote':
			# if user has no previous vote on the question or answer
			if not already_upvoted and not already_downvoted:
				if vote_type == 'up':
					object.upvoters.add(user)
					return HttpResponse(object.upvote_count)

				elif vote_type == 'down':
					object.downvoters.add(user)	
					return HttpResponse(object.downvote_count)

				else:
					return HttpResponse('Error - Unknown vote type')
			else:
				return HttpResponse('Error - Already voted')

		# if user is retracting a vote
		elif vote_action == 'recall-vote':
			if vote_type == 'up' and already_upvoted:
				object.upvoters.remove(user)
				return HttpResponse(object.upvote_count)

			elif vote_type == 'down' and already_downvoted:
				object.downvoters.remove(user)
				return HttpResponse(object.downvote_count)
			else:
				return HttpResponse('Error - Unknown vote type or no vote to recall')
		else:
			return HttpResponse('Error - bad action')
	
	# only upvotes are supported on comments
	elif thread_type == 'question-comment' or thread_type == 'answer-comment':
		already_upvoted = user in object.upvoters.all()

		if vote_action == 'vote':
			if not already_upvoted:
				if vote_type == 'up':
					object.upvoters.add(user)
					return HttpResponse(object.vote_count)
				else:
					return HttpResponse('Error - Unknown vote type')
			else:
				return HttpResponse('Error - Already voted')

		elif vote_action == 'recall-vote':
			if vote_type == 'up' and already_upvoted:
				object.upvoters.remove(user)
				return HttpResponse(object.vote_count)
			else:
				return HttpResponse('Error - Unknown vote type or no vote to recall')
		else:
			return HttpResponse('Error - bad action')


