import django_filters as filters
from django_filters.views import FilterView
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import F
from django.db.models.query import Prefetch
from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import get_language, gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from taggit.models import TaggedItem

from core.constants import (
	REQUIRED_DOWNVOTE_POINTS, ASK_QUESTION_POINTS_CHANGE,
)
from core.mixins import GetObjectMixin
from .forms import (
	AcademicQuestionForm, SchoolQuestionForm, AcademicAnswerForm,
	AcademicQuestionCommentForm, AcademicAnswerCommentForm,
	SchoolQuestionCommentForm, SchoolAnswerCommentForm, SchoolAnswerForm
)
from .mixins import (
	CanEditQuestionMixin, CanDeleteQuestionMixin,
	CanEditAnswerMixin, CanDeleteAnswerMixin,
	CanEditCommentMixin, CanDeleteCommentMixin
)
from .models import (
	SchoolAnswer, SchoolQuestionComment, Subject, AcademicAnswer,
	AcademicQuestion, SchoolQuestion, SchoolAnswerComment,
	AcademicQuestionComment, AcademicAnswerComment
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
		question, poster = self.object, request.user
		poster.site_points = F('site_points') + ASK_QUESTION_POINTS_CHANGE
		poster.save(update_fields=['site_points'])
		
		question.poster = poster
		question.original_language = get_language()
		question.save()	

		return redirect(self.get_success_url())


@method_decorator(login_required, name='post')
class AcademicQuestionDetail(DetailView):
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
				added_result = user.add_answer(question, answer)

				# if answer wasn't added 
				# (if user has attained number of answers limit)
				if not added_result[0]:
					return HttpResponseForbidden(added_result[1])

		# redirect to get request. (SEE Post/Redirect/Get)
		# instead of simply returning to get (return get(self,...))
		return redirect(question.get_absolute_url())

	def get_context_data(self, **kwargs):
		NUM_RELATED_QSTNS = 4
		context = super().get_context_data(**kwargs)
		question, user, all_users = self.object, self.request.user, User.objects.all()

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

		## RELATED QUESTIONS
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
		context['is_following'] = user in question.followers.only('id')
		context['required_downvote_points'] = REQUIRED_DOWNVOTE_POINTS
		context['no_slug_url'] = question.get_absolute_url(with_slug=False)
		context['can_edit_question'] = user.can_edit_question(question)
		context['can_delete_question'] = user.can_delete_question(question)
		
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
		school_question, poster = self.object, request.user
		school_question.school = form.cleaned_data['school']
		poster.site_points = F('site_points') + ASK_QUESTION_POINTS_CHANGE
		poster.save(update_fields=['site_points'])

		school_question.poster = poster
		school_question.original_language = get_language()
		school_question.save()	

		return redirect(self.get_success_url())


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
				answer = get_object_or_404(AcademicAnswer, id=POST.get('answer_id'))
				user.add_answer_comment(answer, comment)

		elif 'add_answer' in POST:
			answer_form = SchoolAnswerForm(POST)
			if answer_form.is_valid():
				answer = answer_form.save(commit=False)
				added_result = user.add_answer(question, answer)

				# if answer wasn't added 
				# (if user has attained number of answers limit)
				if not added_result[0]:
					return HttpResponseForbidden(added_result[1])

		return redirect(question.get_absolute_url())

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
			Prefetch('upvoters', queryset=User.objects.all().only('id'))
		).all()
		comments = question.comments.prefetch_related(
			Prefetch('upvoters', queryset=User.objects.all().only('id'))
		).all()

		context['question_tags'] = question.tags.all()
		context['answers'] = answers
		context['comments'] = comments
		context['num_answers'] = answers.count()
		context['is_following'] = user in question.followers.only('id')
		context['required_downvote_points'] = REQUIRED_DOWNVOTE_POINTS
		context['can_edit_question'] = user.can_edit_question(question)
		context['can_delete_question'] = user.can_delete_question(question)

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
		return self.get_object().question.get_absolute_url()


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
		return self.get_object().question.get_absolute_url()


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

	def get_success_url(self):
		return self.get_object().question.get_absolute_url()


class AcademicAnswerUpdate(AnswerUpdate):
	model = AcademicAnswer

class SchoolAnswerUpdate(AnswerUpdate):
	model = SchoolAnswer


class AnswerDelete(GetObjectMixin, CanDeleteAnswerMixin, DeleteView):
	template_name = 'qa_site/misc/answer_confirm_delete.html'

	def get_success_url(self):
		return self.get_object().question.get_absolute_url()


class AcademicAnswerDelete(AnswerDelete):
	model = AcademicAnswer

class SchoolAnswerDelete(AnswerDelete):
	model = SchoolAnswer

