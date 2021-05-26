from django.shortcuts import render


def index(request):
	""" View function for home page of site. """

	context = {

	}

	# Render the HTML template(page) index.html with the data in the context variable
	return render(request, 'core/index.html', context=context)

