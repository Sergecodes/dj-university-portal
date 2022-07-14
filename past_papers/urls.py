from django.urls import path, include
from django.utils.translation import gettext_lazy as _

from . import views

app_name = 'past_papers'


comment_patterns = [
	path(
        _('<int:pk>/delete/'), 
        views.PastPaperCommentDelete.as_view(), 
        name='past-paper-comment-delete'
    ),
    path(
        _('<int:pk>/edit/'), 
        views.PastPaperCommentUpdate.as_view(), 
        name='past-paper-comment-update'
    ),
]

urlpatterns = [
    path('', views.PastPaperList.as_view(), name='past-paper-list'),
    path(_('upload/'), views.PastPaperCreate.as_view(), name='past-paper-upload'),
	path(_('<int:pk>/delete/'), views.PastPaperDelete.as_view(), name='past-paper-delete'),
    path('<int:pk>/<slug:slug>/', views.PastPaperDetail.as_view(), name='past-paper-detail'),
	path('<int:pk>/', views.PastPaperDetail.as_view(), name='past-paper-detail'),
    path(_('comments/'), include(comment_patterns)),
    path('ajax/past-paper/bookmark/', views.past_paper_bookmark_toggle, name='past-paper-bookmark-toggle'),
]