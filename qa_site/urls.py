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

academic_answer_patterns = [
	path(
		_('<int:pk>/edit/'), 
		views.AcademicAnswerUpdate.as_view(), 
		name='academic-answer-update'
	),
	path(
		_('<int:pk>/delete/'), 
		views.AcademicAnswerDelete.as_view(), 
		name='academic-answer-delete'
	),
]

academic_question_comment_patterns = [
	path(
		_('<int:pk>/edit/'), 
		views.AcademicQuestionCommentUpdate.as_view(), 
		name='academic-question-comment-update'
	),
	path(
		_('<int:pk>/delete/'), 
		views.AcademicQuestionCommentDelete.as_view(), 
		name='academic-question-comment-delete'
	),
]

academic_answer_comment_patterns = [
	path(
		_('<int:pk>/edit/'), 
		views.AcademicAnswerCommentUpdate.as_view(), 
		name='academic-answer-comment-update'
	),
	path(
		_('<int:pk>/delete/'), 
		views.AcademicAnswerCommentDelete.as_view(), 
		name='academic-answer-comment-delete'
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

discuss_comment_patterns = [
	path(
		_('<int:pk>/edit/'), 
		views.DiscussCommentUpdate.as_view(), 
		name='discuss-question-comment-update'
	),
	path(
		_('<int:pk>/delete/'), 
		views.DiscussCommentDelete.as_view(), 
		name='discuss-question-comment-delete'
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

	path('discuss-comments/<int:id>/', ajax.JQueryDiscussCommentDetail.as_view(), name='discuss-comment-rud'),
	path('discuss-comments/', ajax.JQueryDiscussCommentList.as_view(), name='discuss-comments-cl'), # cl: create, list
]


urlpatterns = [
	# these paths should come before the url with a slug
	path('', views.QuestionsExplain.as_view(), name='questions-explain'),
	path(_('academic-questions/'), include(academic_question_patterns)),
	path(_('academic-questions/answers/'), include(academic_answer_patterns)),
	path(_('academic-questions/question-comments/'), include(academic_question_comment_patterns)),
	path(_('academic-questions/answer-comments/'), include(academic_answer_comment_patterns)),
	path(_('discussion-questions/'), include(discuss_question_patterns)),
	path(_('discussion-questions/comments/'), include(discuss_comment_patterns)),

	path('ajax/', include(ajax_patterns))
]