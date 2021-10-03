from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views
from .ajax_views import PhotoUploadView


app_name = 'core'


urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path(_('usage-info/'), views.SiteUsageInfoView.as_view(), name='usage-info'),
    path(_('my-notifications/'), views.NotificationsView.as_view(), name='my-notifs'),

	
    ### AJAX VIEWS ###
	path('ajax/<str:form_for>/upload-photo/', PhotoUploadView.as_view(), name='photo-upload'),
	path('ajax/delete-photo/', PhotoUploadView.as_view(), name='photo-delete'),
]

