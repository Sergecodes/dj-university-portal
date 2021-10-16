"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
# from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.utils.translation import gettext_lazy as _


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# i18n_patterns can only be used in a root urlconf file, 
# will throw ImproperlyConfigured error if used in an included URLconf
urlpatterns += i18n_patterns(
    path('', include('core.urls', namespace='core')),
    path(_('admin/'), admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),  # django-ckeditor
    path(_('flag/'), include('flagging.urls', namespace='flagging')),  
    # path(_('hitcount/'), include('hitcount.urls', namespace='hitcount')),
    path(_('lost-or-found/'), include('lost_and_found.urls', namespace='lost_and_found')),
    path(_('marketplace/'), include('marketplace.urls', namespace='marketplace')),
    path(_('notifications/'), include('notifications.urls', namespace='notifications')),
    path(_('past-papers/'), include('past_papers.urls', namespace='past_papers')),
    path(_('questions/'), include('qa_site.urls', namespace='qa_site')),
    path(_('requested-items/'), include('requested_items.urls', namespace='requested_items')),
    path(_('socialize/'), include('socialize.urls', namespace='socialize')),
    path(_('users/'), include('users.urls', namespace='users')),

) 
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

