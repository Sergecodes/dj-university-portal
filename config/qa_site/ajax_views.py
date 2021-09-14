"""Basically for views that return a JsonResponse"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_POST

from .models import SchoolQuestion, AcademicQuestion


@login_required
@require_POST
def school_question_bookmark_toggle(request):
	"""This view handles bookmarking for school-based questions"""
	user, POST = request.user, request.POST
	id, action = int(POST.get('id')), POST.get('action')
	question = get_object_or_404(SchoolQuestion, pk=id)

	# if vote is new (not removing bookmark)
	if action == 'bookmark':
		user.bookmark_question(question)
		return JsonResponse({'bookmarked': True}, status=200)

	# if user is retracting bookmark
	elif action == 'recall-bookmark':
		user.unbookmark_question(question)
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
		user.bookmark_question(question)
		return JsonResponse({'bookmarked': True}, status=200)

	# if user is retracting bookmark
	elif action == 'recall-bookmark':
		user.unbookmark_question(question)
		return JsonResponse({'unbookmarked': True}, status=200)
	else:
		return JsonResponse({'error': _('Invalid action')}, status=400)

