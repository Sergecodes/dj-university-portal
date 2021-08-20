from django.conf import settings
from django.urls import path, include
from django.utils.translation import ugettext_lazy as _

from . import views, ajax_views

app_name = 'marketplace'

urlpatterns = [
	path('', views.ItemListingList.as_view(), name='item-listing-list'),
	path(_('sell-item/'), views.ItemListingCreate.as_view(), name='item-listing-create'),
	path('<int:pk>/<slug:slug>/', views.ItemListingDetail.as_view(), name='item-listing-detail'),
	path('<int:pk>/', views.ItemListingDetail.as_view(), name='item-listing-detail'),
	path('<slug:slug>/', views.ItemListingDetail.as_view(), name='item-listing-detail'),

	## AJAX VIEWS ##
	path('ajax/get-item-subcategories/', ajax_views.get_item_sub_categories, name='get-item-subcategories'),
	path('ajax/upload-photo/', ajax_views.PhotoUploadView.as_view(), name='photo-upload'),
	path('ajax/delete-photo/', ajax_views.PhotoUploadView.as_view(), name='photo-delete'),

]


# if settings.DEBUG:
# 	import debug_toolbar
# 	urlpatterns = [
# 		path('__debug__/', include(debug_toolbar.urls)),
# 	] + urlpatterns

