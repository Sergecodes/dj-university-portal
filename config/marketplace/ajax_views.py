from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from .forms import ItemListingPhotoForm as ItemPhotoForm
from .models import ItemCategory


@login_required
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

