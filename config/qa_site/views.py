from django_filters.views import FilterView
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import Prefetch
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from taggit.models import TaggedItem

from .forms import (
	AcademicQuestionForm, SchoolQuestionForm
)
from .models import (
	Subject, AcademicAnswer, SchoolAnswer,
	AcademicAnswerComment, SchoolAnswerComment,
	AcademicQuestion, SchoolQuestion, SchoolQuestionTag,
	AcademicQuestionComment, SchoolQuestionComment
)
User = get_user_model()


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


class AcademicQuestionDetail(DetailView):
	model = AcademicQuestion
	context_object_name = 'question'

	def get_context_data(self, **kwargs):
		NUM_RELATED_QSTNS = 4
		context = super().get_context_data(**kwargs)
		question = self.object
		answers = question.answers.prefetch_related(
			'comments', 
			Prefetch('upvoters', queryset=User.objects.all().only('id'))
		).all()
		comments = question.comments.prefetch_related(
			Prefetch('upvoters', queryset=User.objects.all().only('id'))
		).all()

		related_items = TaggedItem.objects.none()
		for tag in question.tags.all():
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
			Prefetch('upvoters', queryset=User.objects.all().only('id')),
			Prefetch('downvoters', queryset=User.objects.all().only('id'))
		) \
		.order_by('-posted_datetime')[:NUM_RELATED_QSTNS]
		
		context['question_tags'] = question.tags.all()
		context['answers'] = answers
		context['comments'] = comments
		context['num_answers'] = answers.count()
		context['related_qstns'] = related_qstns

		return context


class SchoolQuestionCreate(LoginRequiredMixin, CreateView):
	form_class = SchoolQuestionForm
	model = SchoolQuestionForm
	success_url = reverse_lazy('qa_site:academic-question-detail')

	def form_valid(self, form):
		request = self.request
		self.object = form.save(commit=False)
		school_question = self.object
		school_question.school = form.cleaned_data['school']
		school_question.poster = request.user
		school_question.save()	

		return HttpResponseRedirect(self.get_success_url())


@login_required
def vote_academic_thread(request):
	"""
	This view handles upvotes and downvotes for questions, answers and comments of an academic question.
	"""
	user = request.user
	thread_id, thread_type = int(request.POST.get('id')), request.POST.get('thread_type')
	vote_action, vote_type = request.POST.get('action'), request.POST.get('vote_type')
	print(request.POST)
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
					return HttpResponse(object.upvoters.count())

				elif vote_type == 'down':
					object.downvoters.add(user)	
					return HttpResponse(object.downvoters.count())

				else:
					return HttpResponse('Error - Unknown vote type')
			else:
				return HttpResponse('Error - Already voted')

		# if user is retracting a vote
		elif vote_action == 'recall-vote':
			if vote_type == 'up' and already_upvoted:
				object.upvoters.remove(user)
				return HttpResponse(object.upvoters.count())

			elif vote_type == 'down' and already_downvoted:
				object.downvoters.remove(user)
				return HttpResponse(object.downvoters.count())
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
					return HttpResponse(object.upvoters.count())
				else:
					return HttpResponse('Error - Unknown vote type')
			else:
				return HttpResponse('Error - Already voted')

		elif vote_action == 'recall-vote':
			if vote_type == 'up' and already_upvoted:
				object.upvoters.remove(user)
				return HttpResponse(object.upvoters.count())
			else:
				return HttpResponse('Error - Unknown vote type or no vote to recall')
		else:
			return HttpResponse('Error - bad action')


@login_required
def vote_school_thread(request):
    pass

