from django.conf import settings
from django.urls import path, include
from django.utils.translation import ugettext_lazy as _

from . import views

app_name = 'marketplace'

urlpatterns = [
	path('', views.ItemListingList.as_view(), name='listing-list'),
	path(_('sell-item/'), views.create_item_listing, name='listing-create'),
	path('ajax/get-item-subcategories/', views.get_item_sub_categories, name='get-item-subcategories'),
	path('ajax/basic-upload/', views.BasicUploadView.as_view(), name='basic-upload'),
	path('ajax/delete-photo/', views.BasicUploadView.as_view(), name='photo-delete'),
	# path('<int:pk>/<slug:slug>', views.ItemDetail.as_view(), name='listing-detail'),

]


if settings.DEBUG:
	import debug_toolbar
	urlpatterns = [
		path('__debug__/', include(debug_toolbar.urls)),
	] + urlpatterns

