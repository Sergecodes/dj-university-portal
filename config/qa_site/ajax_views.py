"""Basically for views that return a JsonResponse"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_POST
from notifications.signals import notify

from .models import (
	SchoolQuestion, AcademicQuestion, 
	SchoolAnswer, AcademicAnswer,
	SchoolQuestionComment, AcademicQuestionComment,
	SchoolAnswerComment, AcademicAnswerComment
)


def downvote_post(user, post, type):
	"""Helper function to redirect to question or answer downvote"""
	if type == 'question':
		user.downvote_question(post)
	elif type == 'answer':
		user.downvote_answer(post)
	else:
		raise ValueError("Invalid post type")


@login_required
@require_POST
def vote_academic_thread(request):
	"""
	This view handles upvotes and downvotes for questions, answers and comments of an academic question.
	It should be called via client side..
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
		return JsonResponse({
			'success': False,
			'message': _('Invalid thread type')
		}, status=400)

	thread_owner = object.poster

	if thread_type == 'question' or thread_type == 'answer':
		# verify if user has already upvoted and downvoted question or answer
		# only id is important 
		already_upvoted = user in object.upvoters.only('id')
		already_downvoted = user in object.downvoters.only('id')

		# if vote is new (not retracting a previous vote)
		# in frontend, voters won't be displayed.
		if vote_action == 'vote':
			# if user has no previous vote on the question or answer
			if not already_upvoted and not already_downvoted:
				if vote_type == 'up':
					object.upvoters.add(user)

					# send notification to post owner
					notify.send(
						sender=user, 
						recipient=thread_owner, 
						verb=_('liked your question') if thread_type == 'question' else _('liked your answer'),
						target=object
					)
					return JsonResponse({
						'success': True,
						'message': _('Added like')
					}, status=200)

				elif vote_type == 'down':
					downvote_result = downvote_post(user, object, thread_type)

					if not downvote_result[0]:
						return JsonResponse({
							'success': False,
							'message': downvote_result[1]
						}, status=400)

					# send notification to post owner
					notify.send(
						sender=user, 
						recipient=thread_owner, 
						verb=_('disliked your question') if thread_type == 'question' else _('disliked your answer'),
						target=object
					)
					return JsonResponse({
						'success': True,
						'message': _('Added dislike')
					}, status=200)

				else:
					return JsonResponse({
						'success': False,
						'message': _('Unknown vote type')
					}, status=400)

			else:
				return JsonResponse({
					'success': False,
					'message': _('Already voted')
				}, status=400)

		# if user is retracting a vote
		# no notification sent
		elif vote_action == 'recall-vote':
			if vote_type == 'up' and already_upvoted:
				object.upvoters.remove(user)
				return JsonResponse({
					'success': True,
					'message': _('Removed like')
				}, status=200)

			elif vote_type == 'down' and already_downvoted:
				object.downvoters.remove(user)
				return JsonResponse({
					'success': True,
					'message': _('Removed dislike')
				}, status=200)
			else:
				return JsonResponse({
					'success': False,
					'message': _('Unknown vote type or no vote to recall')
				}, status=400)
		else:
			return JsonResponse({
				'success': False,
				'message': _('Bad action')
			}, status=400)
	
	# only upvotes are supported on comments
	elif thread_type == 'question-comment' or thread_type == 'answer-comment':
		already_upvoted = user in object.upvoters.only('id')

		if vote_action == 'vote':
			if not already_upvoted:
				if vote_type == 'up':
					object.upvoters.add(user)
					return JsonResponse({
						'success': True,
						'message': _('Added like')
					}, status=200)
				else:
					return JsonResponse({
						'success': False,
						'message': _('Unknown vote type')
					}, status=400)
			else:
				return JsonResponse({
					'success': False,
					'message': _('Already voted')
				}, status=400)

		elif vote_action == 'recall-vote':
			if vote_type == 'up' and already_upvoted:
				object.upvoters.remove(user)
				return JsonResponse({
					'success': True,
					'message': _('Removed like')
				}, status=200)
			else:
				return JsonResponse({
					'success': False,
					'message': _('Unknown vote type or no vote to recall')
				}, status=400)
		else:
			return JsonResponse({
				'success': False,
				'message': _('Bad action')
			}, status=400)


@login_required
@require_POST
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
		return JsonResponse({
			'success': False,
			'message': _('Invalid thread type')
		}, status=400)

	thread_owner = object.poster

	if thread_type == 'question' or thread_type == 'answer':
		# verify if user has already upvoted and downvoted question or answer
		already_upvoted = user in object.upvoters.only('id')
		already_downvoted = user in object.downvoters.only('id')

		# if vote is new (not retracting a previous vote)
		if vote_action == 'vote':
			# if user has no previous vote on the question or answer
			if not already_upvoted and not already_downvoted:
				if vote_type == 'up':
					object.upvoters.add(user)

					# send notification to post owner
					notify.send(
						sender=user,
						recipient=thread_owner, 
						verb=_('liked your question') if thread_type == 'question' else _('liked your answer'),
						target=object
					)
					return JsonResponse({
							'success': True,
							'message': _('Added like')
						}, status=200)

				elif vote_type == 'down':
					downvote_result = downvote_post(user, object, thread_type)

					if not downvote_result[0]:
						return JsonResponse({
							'success': False,
							'message': downvote_result[1]
						}, status=400)

					# send notification to post owner
					notify.send(
						sender=user, 
						recipient=thread_owner, 
						verb=_('disliked your question') if thread_type == 'question' else _('disliked your answer'),
						target=object
					)
					return JsonResponse({
						'success': True,
						'message': _('Added dislike')
					}, status=200)

				else:
					return JsonResponse({
						'success': False,
						'message': _('Unknown vote type')
					}, status=400)
			else:
				return JsonResponse({
					'success': False,
					'message': _('Already voted')
				}, status=400)

		# if user is retracting a vote
		elif vote_action == 'recall-vote':
			if vote_type == 'up' and already_upvoted:
				object.upvoters.remove(user)
				return JsonResponse({
						'success': True,
						'message': _('Removed like')
					}, status=200)

			elif vote_type == 'down' and already_downvoted:
				object.downvoters.remove(user)
				return JsonResponse({
						'success': True,
						'message': _('Removed dislike')
					}, status=200)
			else:
				return JsonResponse({
						'success': False,
						'message': _('Unknown vote type or no vote to recall')
					}, status=400)
		else:
			return JsonResponse({
				'success': False,
				'message': _('Bad action')
			}, status=400)
	
	# only upvotes are supported on comments
	# no notifications sent to owner of comment
	elif thread_type == 'question-comment' or thread_type == 'answer-comment':
		already_upvoted = user in object.upvoters.only('id')

		if vote_action == 'vote':
			if not already_upvoted:
				if vote_type == 'up':
					object.upvoters.add(user)
					return JsonResponse({
						'success': True,
						'message': _('Added like')
					}, status=200)
				else:
					return JsonResponse({
						'success': False,
						'message': _('Unknown vote type')
					}, status=400)
			else:
				return JsonResponse({
					'success': False,
					'message': _('Already voted')
				}, status=400)

		elif vote_action == 'recall-vote':
			if vote_type == 'up' and already_upvoted:
				object.upvoters.remove(user)
				return JsonResponse({
					'success': True,
					'message': _('Removed like')
				}, status=200)
			else:
				return JsonResponse({
						'success': False,
						'message': _('Unknown vote type or no vote to recall')
					}, status=400)
		else:
			return JsonResponse({
				'success': False,
				'message': _('Bad action')
			}, status=400)


@login_required
@require_POST
def school_question_bookmark_toggle(request):
	"""This view handles bookmarking for school-based questions"""
	user, POST = request.user, request.POST
	id, action = int(POST.get('id')), POST.get('action')
	question = get_object_or_404(SchoolQuestion, pk=id)

	# if vote is new (not removing bookmark)
	if action == 'bookmark':
		question.bookmarkers.add(user)
		return JsonResponse({'bookmarked': True}, status=200)

	# if user is retracting bookmark
	elif action == 'recall-bookmark':
		question.bookmarkers.remove(user)
		return JsonResponse({'unbookmarked': True}, status=200)
	else:
		return JsonResponse({'error': _('Invalid action')}, status=400)


@login_required
@require_POST
def academic_question_bookmark_toggle(request):
	"""This view handles bookmarking for academic questions"""
	user, POST = request.user, request.POST
	id, action = int(POST.get('id')), POST.get('action')
	question = get_object_or_404(AcademicQuestion, pk=id)

	# if vote is new (not removing bookmark)
	if action == 'bookmark':
		question.bookmarkers.add(user)
		return JsonResponse({'bookmarked': True}, status=200)

	# if user is retracting bookmark
	elif action == 'recall-bookmark':
		question.bookmarkers.remove(user)
		return JsonResponse({'unbookmarked': True}, status=200)
	else:
		return JsonResponse({'error': _('Invalid action')}, status=400)

