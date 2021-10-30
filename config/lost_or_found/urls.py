from django.urls import path, include
from django.utils.translation import gettext_lazy as _

from . import views, ajax_views

app_name = 'lost_or_found'


lost_items_patterns = [
	path('', views.LostItemList.as_view(), name='lost-item-list'),
	path(_('report-lost-item/'), views.LostItemCreate.as_view(), name='lost-item-create'),
	path(_('<int:pk>/edit/'), views.LostItemUpdate.as_view(), name='lost-item-update'),
	path(_('<int:pk>/delete/'), views.LostItemDelete.as_view(), name='lost-item-delete'),
	path('<int:pk>/<slug:slug>/', views.LostItemDetail.as_view(), name='lost-item-detail'),
	path('<int:pk>/', views.LostItemDetail.as_view(), name='lost-item-detail'),
]

found_items_patterns = [
	path('', views.FoundItemList.as_view(), name='found-item-list'),
	path(_('report-found-item/'), views.FoundItemCreate.as_view(), name='found-item-create'),
	path(_('<int:pk>/edit/'), views.FoundItemUpdate.as_view(), name='found-item-update'),
	path(_('<int:pk>/delete/'), views.FoundItemDelete.as_view(), name='found-item-delete'),
	path('<int:pk>/<slug:slug>/', views.FoundItemDetail.as_view(), name='found-item-detail'),
	path('<int:pk>/', views.FoundItemDetail.as_view(), name='found-item-detail'),
]

ajax_patterns = [
	path(
		'lost-items/bookmark/', 
		ajax_views.lost_item_bookmark_toggle, 
		name='lost-item-bookmark-toggle'
	),
	path(
		'found-items/bookmark/', 
		ajax_views.found_item_bookmark_toggle, 
		name='found-item-bookmark-toggle'
	),
]


urlpatterns = [
	path(_('lost-items/'), include(lost_items_patterns)),
	path(_('found-items/'), include(found_items_patterns)),
	path('ajax/', include(ajax_patterns))
]
