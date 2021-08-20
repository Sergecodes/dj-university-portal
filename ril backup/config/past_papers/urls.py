from django.conf import settings
from django.urls import path, include
from django.utils.translation import ugettext_lazy as _

from . import views

app_name = 'past_papers'


urlpatterns = [
    path(_('upload/'), views.PastPaperCreateView.as_view(), name='past-paper-upload'),

]