from django.urls import path, include
from django.utils.translation import gettext_lazy as _

from . import views, ajax_views

app_name = 'marketplace'


item_listing_patterns = [
	path('', views.ItemListingList.as_view(), name='item-listing-list'),
	path(_('sell-an-item/'), views.ItemListingCreate.as_view(), name='item-listing-create'),
	path(_('<int:pk>/edit/'), views.ItemListingUpdate.as_view(), name='item-listing-update'),
	path(_('<int:pk>/delete/'), views.ItemListingDelete.as_view(), name='item-listing-delete'),
	path('<int:pk>/<slug:slug>/', views.ItemListingDetail.as_view(), name='item-listing-detail'),
	path('<int:pk>/', views.ItemListingDetail.as_view(), name='item-listing-detail'),
]

ad_listing_patterns = [
	path('', views.AdListingList.as_view(), name='ad-listing-list'),
	path(_('advertize/'), views.AdListingCreate.as_view(), name='ad-listing-create'),
	path(_('<int:pk>/edit/'), views.AdListingUpdate.as_view(), name='ad-listing-update'),
	path(_('<int:pk>/delete/'), views.AdListingDelete.as_view(), name='ad-listing-delete'),
	path('<int:pk>/<slug:slug>/', views.AdListingDetail.as_view(), name='ad-listing-detail'),
	path('<int:pk>/', views.AdListingDetail.as_view(), name='ad-listing-detail'),
]

ajax_patterns = [
	path('items/bookmark/', ajax_views.item_bookmark_toggle, name='item-bookmark-toggle'),
	path('adverts/bookmark/', ajax_views.ad_bookmark_toggle, name='ad-bookmark-toggle'),
	path('get-item-subcategories/', ajax_views.get_item_sub_categories, name='get-item-subcategories'),
]


urlpatterns = [
	path(_('items/'), include(item_listing_patterns)),
	path(_('adverts/'), include(ad_listing_patterns)),
	path('ajax/', include(ajax_patterns))
]
