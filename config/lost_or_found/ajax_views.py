from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .models import LostItem, FoundItem


@login_required
@require_POST
def lost_item_bookmark_toggle(request):
	"""This view handles bookmarking for lost items"""
	user, POST = request.user, request.POST
	id, action = POST.get('id'), POST.get('action')
	lost_item = get_object_or_404(LostItem, pk=id)

	# if vote is new (not removing bookmark)
	if action == 'bookmark':
		lost_item.bookmarkers.add(user)
		return JsonResponse({'bookmarked': True,}, status=200)

	# if user is retracting bookmark
	elif action == 'recall-bookmark':
		lost_item.bookmarkers.remove(user)
		return JsonResponse({'unbookmarked': True}, status=200)
	else:
		return JsonResponse({'error': _('Invalid action')}, status=400)


@login_required
@require_POST
def found_item_bookmark_toggle(request):
	"""This view handles bookmarking for found items"""
	user, POST = request.user, request.POST
	id, action = POST.get('id'), POST.get('action')
	found_item = get_object_or_404(FoundItem, pk=id)

	# if vote is new (not removing bookmark)
	if action == 'bookmark':
		found_item.bookmarkers.add(user)
		return JsonResponse({'bookmarked': True}, status=200)

	# if user is retracting bookmark
	elif action == 'recall-bookmark':
		found_item.bookmarkers.remove(user)
		return JsonResponse({'unbookmarked': True}, status=200)
	else:
		return JsonResponse({'error': _('Invalid action')}, status=400)


