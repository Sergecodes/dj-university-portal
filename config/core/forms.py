from crispy_forms.layout import LayoutObject
from django.template.loader import render_to_string


class PhotoFormLayout(LayoutObject):
	""" 
	Render the the photo upload template, as though it were a Field.
	Accepts the names (as a string) of template to use.
	Used to insert item listing & ad photo upload templates into their respective forms.

	Examples:
		PhotoFormLayout('photo_form')
		PhotoFormLayout('photo_form', template='...')
		PhotoFormLayout('photo_form', template='...', extra_context={...})
	"""

	template = 'core/photos_upload.html'
	extra_context = {}

	def __init__(self, template=None, *args, **kwargs):
		# retrieve and store extra context
		# if extra_context isn't found, use the class variable extra_context (hence the self.extra_context)
		self.extra_context = kwargs.pop('extra_context', self.extra_context)

		# Override class variable with an instance level variable
		if template:
			print(template)
			self.template = template
		
	def render(self, form, form_style, context, **kwargs):
		if self.extra_context:
			context.update(self.extra_context)
		# context is a list. context.flatten() converts it to a dict
		return render_to_string(self.template, context.flatten())

