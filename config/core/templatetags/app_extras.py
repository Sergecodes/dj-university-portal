import bleach
import uuid
from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template.defaultfilters import stringfilter
from django.utils.translation import gettext_lazy as _

from users.utils import parse_phone_number

register = template.Library()

register.filter('parse_tel', parse_phone_number)

@register.filter(name='zip')
def zip_lists(list1, list2):
	return zip(list1, list2)
 
 
@register.filter
def remove_tags(text_body):
	"""Strip html tags from `text_body` using the `clean` library. Django says `striptags` method isn't guaranteed to produce safe output and thus `safe` should never be applied to its output."""
	return bleach.clean(text_body, tags=[], strip=True)


@register.simple_tag
def query_transform(request, **kwargs):
	"""Insert kwargs into url"""
	updated = request.GET.copy()
	for k, v in kwargs.items():
		if v is not None:
			updated[k] = v
		else:
			updated.pop(k, 0)

	return updated.urlencode()


@register.simple_tag(name='get_login_url')
def get_login_url():
	login_url = getattr(settings, 'LOGIN_URL', None)
	if not login_url:
		raise ImproperlyConfigured(_('LOGIN_URL is not defined in the settings'))
	if not login_url.endswith('/'):
		login_url += '/'
	return login_url


@register.inclusion_tag('core/social_share_tooltip.html')
def render_social_share_tooltip(object, post_type, use_name='post'):
	"""
	A template tag used for adding social media share tooltip in templates.
	This tag is used to generate a unique id for each rendered tooltip
	"""
	context = {}

	# generate random id for each tooltip
	# in case there are many tooltips on the page...
	context['random_uid'] = str(uuid.uuid4()).split('-')[0]
	context['use_name'] = use_name

	objects_with_slug = ('lost-item', 'found-item', 'past-paper', 'academic-question')
	if post_type in objects_with_slug:
		# get url without slug
		context['object_url'] = object.get_absolute_url(with_slug=False)
	else:
		# get normal url (which doesn't contain slug. such as school-based-question)
		context['object_url'] = object.get_absolute_url()

	return context

# @register.filter
# def parse_tel(value):
#     """
#     Appropriately print a phone number.
#     e.g. 651234566 should return 6 51 23 45 66
#     """
#     result = value[0]
#     n = len(value)
#     for i in range(1, n, 2):
#         temp = value[i] + value[i+1]
#         result = result + ' ' + temp

#     return result