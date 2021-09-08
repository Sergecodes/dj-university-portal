from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = 'socialize'

urlpatterns = [
    path(_('create-social-profile/'), views.SocialProfileCreate.as_view(), name='create-profile'),
    path(_('find-friend/'), views.friend_finder, name='find-friend'),
    path(_('find-friend/results/'), views.SocialProfileList.as_view(), name='display-results'),
    path(_('<str:username>/update-social-profile/'), views.SocialProfileUpdate.as_view(), name='update-profile'),

]