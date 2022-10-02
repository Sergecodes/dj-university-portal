
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, LayoutObject, Row, Column, Submit
from django import forms
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


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
			# print(template)
			self.template = template
		
	def render(self, form, form_style, context, **kwargs):
		if self.extra_context:
			context.update(self.extra_context)
		# context is a list. context.flatten() converts it to a dict
		return render_to_string(self.template, context.flatten())


class ContactForm(forms.Form):
	name = forms.CharField(label=_('Your name'), max_length=100)
	email = forms.EmailField(label=_('Your email address'))
	subject = forms.CharField(label=_('Subject'), max_length=100)
	message = forms.CharField(
		label=_('Message'), 
		widget=forms.Textarea(attrs={'rows': 5}), 
		max_length=2000
	)

	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)

		if user:
			self.fields['email'].initial = user.email 

		self.helper = FormHelper()
		self.helper.layout = Layout(
			Row(
				Column('name', css_class='form-group col-md-6'),
				Column('email', css_class='form-group col-md-6'),
				css_class='form-row'
			),
			'subject',
			'message',
			Submit('submit', _('Send'), css_class="mt-3 btn-warning")
		)
