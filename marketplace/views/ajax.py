"""Basically for views that return a JsonResponse"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_POST

from ..models import ItemCategory, ItemListing, AdListing


@login_required
@require_POST
def item_bookmark_toggle(request):
	"""This view handles bookmarking for item listings"""
	user, POST = request.user, request.POST
	id, action = POST.get('id'), POST.get('action')
	listing = get_object_or_404(ItemListing, pk=id)

	# if vote is new (not removing bookmark)
	if action == 'bookmark':
		listing.bookmarkers.add(user)
		return JsonResponse({
			'bookmarked': True,
			# coerce _('foo') (__proxy__ ) to string to permit concatenation
			# 'content': str(bookmark_count) + ' ' + (str(_('bookmarks')) if bookmark_count > 1 else str(_('bookmark')))
		}, status=200)

	# if user is retracting bookmark
	elif action == 'recall-bookmark':
		listing.bookmarkers.remove(user)
		return JsonResponse({'unbookmarked': True}, status=200)
	else:
		return JsonResponse({'error': _('Invalid action')}, status=400)


@login_required
@require_POST
def ad_bookmark_toggle(request):
	"""This view handles bookmarking for ad listings"""
	user, POST = request.user, request.POST
	id, action = POST.get('id'), POST.get('action')
	listing = get_object_or_404(AdListing, pk=id)

	# if vote is new (not removing bookmark)
	if action == 'bookmark':
		listing.bookmarkers.add(user)
		return JsonResponse({'bookmarked': True}, status=200)

	# if user is retracting bookmark
	elif action == 'recall-bookmark':
		listing.bookmarkers.remove(user)
		return JsonResponse({'unbookmarked': True}, status=200)
	else:
		return JsonResponse({'error': _('Invalid action')}, status=400)


@login_required
@require_GET
def get_item_sub_categories(request):
	"""Return the sub categories of a given item category via ajax"""

	# no need to coerce, get_object_or_404 handles coercion
	category_pk = request.GET.get('category_id')  

	if not category_pk:
		return JsonResponse({'sub_categories': []})

	category = get_object_or_404(ItemCategory, pk=category_pk)
	result = {
		# get id and name of each sub category in list
		'sub_categories': list(category.sub_categories.values('id', 'name'))
	}

	return JsonResponse(result)

