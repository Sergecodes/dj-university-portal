from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

app_name = 'marketplace'

urlpatterns = [
	path('', views.ItemList.as_view(), name='item-list'),
	path('<int:pk>/<slug:slug>', views.ItemDetail.as_view(), name='item-detail'),

]

# The following line is used to serve media files (only in development.)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
	import debug_toolbar
	urlpatterns = [
		path('__debug__/', include(debug_toolbar.urls)),
	] + urlpatterns

