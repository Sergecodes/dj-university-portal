from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy
from django.utils.translation import gettext_lazy as _

from .views import views, ajax

app_name = 'users'


profile_patterns = [
	path('', views.Dashboard.as_view(), name='profile-dashboard'),
	path(_('dashboard/'), views.Dashboard.as_view(), name='profile-dashboard'),
	path(_('marketplace/'), views.Marketplace.as_view(), name='profile-marketplace'),
	path(_('questions-and-answers/'), views.QuestionsAndAnswers.as_view(), name='profile-qa'),
	path(_('lost-or-found/'), views.LostAndFound.as_view(), name='profile-lostfound'),
	path(_('past-papers/'), views.PastPaper.as_view(), name='profile-pastpapers'),
	path(_('requested-items/'), views.RequestedItems.as_view(), name='profile-requested'),
	path(_('bookmarked-profiles/'), views.BookmarkedSocialProfiles.as_view(), name='profile-bookmarkedprofiles'),

]


urlpatterns = [
	path(_('profile/'), include(profile_patterns)),
	path(_('register/'), views.UserCreate.as_view(), name='register'),
	path(_('confirm-email/<uidb64>/<token>/'), views.activate_account, name='account-activate'),
	path(
		_('login/'),
		auth_views.LoginView.as_view(
			template_name='users/auth/login.html',
			# see warning concerning this boolean attribute 
			# https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.LoginView
			redirect_authenticated_user=True
		), 
		name='login'
	),
	path(
		_('logout/'), 
		auth_views.LogoutView.as_view(),
		name='logout'
	),
	# path(
	# 	_('logout_then_login/'),
	# 	views.logout_and_login,
	# 	name='logout-then-login'
	# ),
	# path(
	# 	_('change-password/'),
	# 	auth_views.PasswordChangeView.as_view(
	# 		template_name='users/auth/password_change.html',
	# 		success_url=reverse_lazy('users:password-change-done')
	# 	),
	# 	name='password-change'
	# ),
	path(
		_('change-password/'),
		views.PasswordChangeView.as_view(
			template_name='users/auth/password_change.html',
			success_url=reverse_lazy('users:password-change-done')
		),
		name='password-change'
	),
	path(
		_('change-password/done/'),
		auth_views.PasswordChangeDoneView.as_view(
			template_name='users/auth/password_change_done.html',
		),
		name='password-change-done'
	),
	# note that both authed and unauthed users can access this view. of course! 
	# a previously authed user might have forgotten his password, same as an unauthed user.
	# path(
	# 	_('reset-password/'),
	# 	auth_views.PasswordResetView.as_view(
	# 		template_name='users/auth/password_reset_form.html',
	# 		email_template_name='users/auth/password_reset_email.html',
	# 		success_url=reverse_lazy('users:password-reset-done')
	# 	),
	# 	name='password-reset'
	# ),
	path(
		_('reset-password/'),
		views.PasswordResetView.as_view(
			template_name='users/auth/password_reset_form.html',
			email_template_name='users/auth/password_reset_email.html',
			success_url=reverse_lazy('users:password-reset-done')
		),
		name='password-reset'
	),
	path(
		# The page shown after a user has been emailed a link to reset their password.
		_('reset-password/email-sent/'),
		auth_views.PasswordResetDoneView.as_view(
			template_name='users/auth/password_reset_done.html',
		),
		name='password-reset-done'
	),
	path(
		# Presents a form for entering a new password.
		_('reset-password/confirm/<uidb64>/<token>/'),
		auth_views.PasswordResetConfirmView.as_view(
			template_name='users/auth/password_reset_confirm.html',
			success_url=reverse_lazy('users:password-reset-complete')
		),
		name='password-reset-confirm'
	),
	path(
		# Presents a view which informs the user that the password has been successfully changed.
		_('reset-password/complete/'),
		auth_views.PasswordResetCompleteView.as_view(
			template_name='users/auth/password_reset_complete.html',
		),
		name='password-reset-complete'
	),
	path(_('<str:username>/edit-profile/'), views.UserUpdate.as_view(), name='edit-profile'),

]



# Class-based password reset views
# - PasswordResetView sends the mail
# - PasswordResetDoneView shows a success message for the above
# - PasswordResetConfirmView checks the link the user clicked and
#   prompts for a new password
# - PasswordResetCompleteView shows a success message for the above