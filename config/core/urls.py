from django.urls import path

from .ajax_views import PhotoUploadView


app_name = 'core'

urlpatterns = [
    
    ### AJAX VIEWS ###
	path('ajax/<str:form_for>/upload-photo/', PhotoUploadView.as_view(), name='photo-upload'),
	path('ajax/delete-photo/', PhotoUploadView.as_view(), name='photo-delete'),
]

