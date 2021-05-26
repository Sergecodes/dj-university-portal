from allauth.account.adapter import DefaultAccountAdapter


class MyAccountAdapter(DefaultAccountAdapter):

	def get_login_redirect_url(self, request):
		pass
	# path = f"/accounts/{username}/"
	# return path.format(username=request.user.username)
