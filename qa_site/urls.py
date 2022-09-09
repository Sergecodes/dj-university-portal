from django.urls import path, include
from django.utils.translation import gettext_lazy as _

from .views import views, ajax

app_name = 'qa_site'


academic_question_patterns = [
	path(
		'',
		views.AcademicQuestionList.as_view(),
		name='academic-question-list'
	),
	path(
		_('ask/'), 
		views.AcademicQuestionCreate.as_view(), 
		name='academic-question-create'
	),
	path(
		_('<int:pk>/edit/'), 
		views.AcademicQuestionUpdate.as_view(), 
		name='academic-question-update'
	),
	path(
		_('<int:pk>/delete/'), 
		views.AcademicQuestionDelete.as_view(), 
		name='academic-question-delete'
	),
	path(
		'<int:pk>/<slug:slug>/', 
		views.AcademicQuestionDetail.as_view(), 
		name='academic-question-detail'
	),
	path(
		'<int:pk>/', 
		views.AcademicQuestionDetail.as_view(), 
		name='academic-question-detail'
	),
]

discuss_question_patterns = [
	path(
		'',
		views.DiscussQuestionList.as_view(),
		name='discuss-question-list'
	),
	path(
		_('ask/'), 
		views.DiscussQuestionCreate.as_view(), 
		name='discuss-question-create'
	),
	path(
		_('<int:pk>/edit/'), 
		views.DiscussQuestionUpdate.as_view(), 
		name='discuss-question-update'
	),
	path(
		_('<int:pk>/delete/'), 
		views.DiscussQuestionDelete.as_view(), 
		name='discuss-question-delete'
	),
	
	# no slug for discussion questions coz they have no title
	path(
		'<int:pk>/', 
		views.DiscussQuestionDetail.as_view(), 
		name='discuss-question-detail'
	),
]

ajax_patterns = [
	path('academic-thread/vote/', ajax.vote_academic_thread, name='academic-thread-vote'),
	path('discuss-thread/vote/', ajax.vote_discuss_thread, name='discuss-thread-vote'),
	path('discuss-question/bookmark/', ajax.discuss_question_bookmark_toggle, name='discuss-bookmark-toggle'),
	path('academic-question/bookmark/', ajax.academic_question_bookmark_toggle, name='academic-bookmark-toggle'),
	path('academic-question/follow/', ajax.academic_question_follow_toggle, name='academic-follow-toggle'),
	path('discuss-question/follow/', ajax.discuss_question_follow_toggle, name='discuss-follow-toggle'),
	path('users-mentioned/<int:question_id>/', ajax.get_users_mentioned, name='users-mentioned'),

	path('comments/<str:model_name>/<int:id>/', ajax.JQueryCommentDetail.as_view(), name='comment-rud'),
	path('comments/<str:model_name>/', ajax.JQueryCommentList.as_view(), name='comments-cl'), # cl: create, list
]


urlpatterns = [
	# these paths should come before the url with a slug
	path('', views.QuestionsExplain.as_view(), name='questions-explain'),
	path(_('academic-questions/'), include(academic_question_patterns)),
	path(_('discussion-questions/'), include(discuss_question_patterns)),

	path('ajax/', include(ajax_patterns))
]