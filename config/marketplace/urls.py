from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.utils.translation import ugettext_lazy as _

from . import views

app_name = 'marketplace'

urlpatterns = [
	path('', views.ItemListingList.as_view(), name='listing-list'),
	path(_('sell-item/'), views.create_item_listing, name='listing-create'),
	# path('<int:pk>/<slug:slug>', views.ItemDetail.as_view(), name='listing-detail'),

]

# The following line is used to serve media files (only in development.)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
	import debug_toolbar
	urlpatterns = [
		path('__debug__/', include(debug_toolbar.urls)),
	] + urlpatterns

