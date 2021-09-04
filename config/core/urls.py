from django.conf import settings
from django.urls import path, include

from .ajax_views import PhotoUploadView
from .views import HomePageView

app_name = 'core'

urlpatterns = [
    
    ### AJAX VIEWS ###
	path('ajax/<str:form_for>/upload-photo/', PhotoUploadView.as_view(), name='photo-upload'),
	path('ajax/delete-photo/', PhotoUploadView.as_view(), name='photo-delete'),
]

