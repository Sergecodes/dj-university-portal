from django.urls import path, include
from django.utils.translation import gettext_lazy as _

from . import views, ajax_views

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
		_('<int:pk>/<slug:slug>/'), 
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

school_question_patterns = [
	path(
		'',
		views.SchoolQuestionList.as_view(),
		name='school-question-list'
	),
	path(
		_('ask/'), 
		views.SchoolQuestionCreate.as_view(), 
		name='school-question-create'
	),
	path(
		_('<int:pk>/edit/'), 
		views.SchoolQuestionUpdate.as_view(), 
		name='school-question-update'
	),
	path(
		_('<int:pk>/delete/'), 
		views.SchoolQuestionDelete.as_view(), 
		name='school-question-delete'
	),
	
	# no slug for school-based questions coz they have no title
	path(
		'<int:pk>/', 
		views.SchoolQuestionDetail.as_view(), 
		name='school-question-detail'
	),
]

school_answer_patterns = [
	path(
		_('<int:pk>/edit/'), 
		views.SchoolAnswerUpdate.as_view(), 
		name='school-answer-update'
	),
	path(
		_('<int:pk>/delete/'), 
		views.SchoolAnswerDelete.as_view(), 
		name='school-answer-delete'
	),
]

school_question_comment_patterns = [
	path(
		_('<int:pk>/edit/'), 
		views.SchoolQuestionCommentUpdate.as_view(), 
		name='school-question-comment-update'
	),
	path(
		_('<int:pk>/delete/'), 
		views.SchoolQuestionCommentDelete.as_view(), 
		name='school-question-comment-delete'
	),
]

school_answer_comment_patterns = [
	path(
		_('<int:pk>/edit/'), 
		views.SchoolAnswerCommentUpdate.as_view(), 
		name='school-answer-comment-update'
	),
	path(
		_('<int:pk>/delete/'), 
		views.SchoolAnswerCommentDelete.as_view(), 
		name='school-answer-comment-delete'
	),
]


ajax_patterns = [
	path('academic-thread/vote/', ajax_views.vote_academic_thread, name='academic-thread-vote'),
	path('school-thread/vote/', ajax_views.vote_school_thread, name='school-thread-vote'),
	path('school-question/bookmark/', ajax_views.school_question_bookmark_toggle, name='school-bookmark-toggle'),
	path('academic-question/bookmark/', ajax_views.academic_question_bookmark_toggle, name='academic-bookmark-toggle'),
	path('academic-question/follow/', ajax_views.academic_question_follow_toggle, name='academic-follow-toggle'),
	path('school-question/follow/', ajax_views.school_question_follow_toggle, name='school-follow-toggle'),
]


urlpatterns = [
	# these paths should come before the url with a slug
	path('', views.QuestionsExplain.as_view(), name='questions-explain'),
	path(_('academic-questions/'), include(academic_question_patterns)),
	path(_('academic-questions/answers/'), include(academic_answer_patterns)),
	path(_('academic-questions/question-comments/'), include(academic_question_comment_patterns)),
	path(_('academic-questions/answer-comments/'), include(academic_answer_comment_patterns)),
	path(_('school-based-questions/'), include(school_question_patterns)),
	path(_('school-based-questions/answers/'), include(school_answer_patterns)),
	path(_('school-based-questions/question-comments/'), include(school_question_comment_patterns)),
	path(_('school-based-questions/answer-comments/'), include(school_answer_comment_patterns)),

	path('ajax/', include(ajax_patterns))
]