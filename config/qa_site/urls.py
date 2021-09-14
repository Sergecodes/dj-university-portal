from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views, ajax_views


app_name = 'qa_site'

urlpatterns = [
	# these paths should come before the url with a slug
	path('', views.QuestionsExplain.as_view(), name='questions-explain'),
	path(
		_('academic-questions/'),
		views.AcademicQuestionList.as_view(),
		name='academic-question-list'
	),
	path(
		_('academic-questions/ask/'), 
		views.AcademicQuestionCreate.as_view(), 
		name='academic-question-create'
	),
	path(
		_('school-based-questions/'),
		views.SchoolQuestionList.as_view(),
		name='school-question-list'
	),
	path(
		_('school-based-questions/ask/'), 
		views.SchoolQuestionCreate.as_view(), 
		name='school-question-create'
	),
	path(
		_('academic-questions/<int:pk>/<slug:slug>/'), 
		views.AcademicQuestionDetail.as_view(), 
		name='academic-question-detail'
	),
	path(
		_('academic-questions/<int:pk>/'), 
		views.AcademicQuestionDetail.as_view(), 
		name='academic-question-detail'
	),
	# no slug for school-based questions coz they have no title
	path(
		_('school-based-questions/<int:pk>/'), 
		views.SchoolQuestionDetail.as_view(), 
		name='school-question-detail'
	),

	## AJAX VIEWS
	path('ajax/academic-thread/vote/', views.vote_academic_thread, name='academic-thread-vote'),
	path('ajax/school-thread/vote/', views.vote_school_thread, name='school-thread-vote'),
	path('ajax/school-question/bookmark/', ajax_views.school_question_bookmark_toggle, name='school-bookmark-toggle'),
	path('ajax/academic-question/bookmark/', ajax_views.academic_question_bookmark_toggle, name='academic-bookmark-toggle'),
]