from django.conf import settings
from django.urls import path, include
from django.utils.translation import ugettext_lazy as _

from . import views

app_name = 'past_papers'


urlpatterns = [
    path('', views.PastPaperList.as_view(), name='past-paper-list'),
    path(_('upload/'), views.PastPaperCreate.as_view(), name='past-paper-upload'),
    path(_('<int:pk>/<slug:slug>/'), views.PastPaperDetail.as_view(), name='past-paper-detail'),
	path(_('<int:pk>/'), views.PastPaperDetail.as_view(), name='past-paper-detail'),

]