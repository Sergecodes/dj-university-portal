from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views, ajax_views


app_name = 'marketplace'

urlpatterns = [
	path('', views.ListingsExplain.as_view(), name='listings-explain'),

	## ITEM LISTING ##
	path(_('items/'), views.ItemListingList.as_view(), name='item-listing-list'),
	path(_('items/sell-an-item/'), views.ItemListingCreate.as_view(), name='item-listing-create'),
	path(_('items/<int:pk>/<slug:slug>/'), views.ItemListingDetail.as_view(), name='item-listing-detail'),
	path(_('items/<int:pk>/'), views.ItemListingDetail.as_view(), name='item-listing-detail'),

	## AD LISTING ##
	path(_('adverts/'), views.AdListingList.as_view(), name='ad-listing-list'),
	path(_('adverts/advertize/'), views.AdListingCreate.as_view(), name='ad-listing-create'),
	path(_('adverts/<int:pk>/<slug:slug>/'), views.AdListingDetail.as_view(), name='ad-listing-detail'),
	path(_('adverts/<int:pk>/'), views.AdListingDetail.as_view(), name='ad-listing-detail'),

	## AJAX VIEWS ##
	path('ajax/get-item-subcategories/', ajax_views.get_item_sub_categories, name='get-item-subcategories'),
]
