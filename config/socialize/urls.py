from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from . import views

app_name = 'socialize'

urlpatterns = [
    path(_('activate-account/'), views.SocialProfileCreate.as_view(), name='socialize-activate')
]