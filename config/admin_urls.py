from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
	path('ckeditor/', include('ckeditor_uploader.urls')),
] + i18n_patterns(path('', admin.site.urls)) \
	+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # used to serve media files in development only

# (surely use whitenoise plus a cdn like cloudfront in production)) : see stackoverflow.com/questions/37376289


if settings.DEBUG:
	import debug_toolbar
	urlpatterns = [
		path('__debug__/', include(debug_toolbar.urls)),
	] + urlpatterns
