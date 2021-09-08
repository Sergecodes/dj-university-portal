from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views


app_name = 'qa_site'

urlpatterns = [
	# these should come before the url with a slug
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
	path(
		_('school-based-questions/<int:pk>/'), 
		views.SchoolQuestionDetail.as_view(), 
		name='school-question-detail'
	),

	# VOTES #
	path('ajax/academic-thread/vote/', views.vote_academic_thread, name='academic-thread-vote'),
	path('ajax/school-thread/vote/', views.vote_school_thread, name='school-thread-vote'),

]