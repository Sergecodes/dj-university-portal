from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import RedirectView

from .views import views, ajax 

app_name = 'core'


urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    # redirect home/ to '/'
    path(_('home/'), RedirectView.as_view(url='/')),
    path(_('site-usage/info/'), views.SiteUsageInfoView.as_view(), name='usage-info'),
    path(_('my-notifications/'), views.NotificationsView.as_view(), name='my-notifs'),
    path(_('privacy-policy/'), views.PrivacyPolicyView.as_view(), name='privacy-policy'),
    path(_('terms-and-conditions/'), views.TermsAndConditionsView.as_view(), name='terms-conditions'),
    path(_('search/'), views.search_site, name='site-search'),
    path(_('search/<str:category>/'), views.get_category_search_results, name='category-search'),
    path(_('set-session-country/<str:country_code>/'), views.set_session_country, name='set-session-country'),
    path(_('set-session-country/'), views.set_session_country, name='set-session-country'),
	
    ### AJAX VIEWS ###
	path('ajax/<str:form_for>/upload-photo/', ajax.PhotoUploadView.as_view(), name='photo-upload'),
	path('ajax/delete-photo/', ajax.PhotoUploadView.as_view(), name='photo-delete'),
]

