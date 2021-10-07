import bleach
from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.template.defaultfilters import stringfilter
from django.utils.translation import gettext_lazy as _

from core.utils import parse_phone_number, is_mobile
# i imported the User module directly; this was to ensure that the User methods will work.
# and identified by the code editor; xD
# just allow it as-is.
from users.models import User

register = template.Library()


register.filter('is_mobile', is_mobile)
register.filter('parse_tel', parse_phone_number)

## register qa_site editing and deleting methods
register.filter(User.can_edit_comment)
register.filter(User.can_delete_comment)
register.filter(User.can_edit_answer)
register.filter(User.can_delete_answer)


@register.filter
def get_model_name(obj):
	return type(obj).__name__

@register.filter
def get_app_name(obj):
	return obj._meta.app_label

@register.filter
def post_is_unread(user_notifs_group, post):
	"""Return whether post has any unread notifications or not."""
	# first get unread user notifications from the category
	unread_group_notifs = user_notifs_group.unread()

	# now get(lazily) notifications(unread) that concern the post
	post_unread_notifs = unread_group_notifs.filter(
		target_object_id=post.id,
		target_content_type=ContentType.objects.get_for_model(post)
	)

	# if any notification concerning the post is found, return True
	if post_unread_notifs.exists():
		return True
	return False


@register.filter(name='zip')
def zip_lists(list1, list2):
	return zip(list1, list2)

 
@register.filter
def remove_tags(text_body):
	"""
	Strip html tags from `text_body` using the `clean` library. 
	Django says `striptags` method isn't guaranteed to produce safe output 
	and thus `safe` should never be applied to its output.
	"""
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


@register.inclusion_tag('core/bookmarking.html')
def render_bookmark_template(
	object, 
	bookmark_url, 
	title_text=_('Add this post to your favourites. (click again to undo)')
):
	bookmarkers = object.bookmarkers.only('id')
	
	return {
		'object_id': object.id,
		'bookmarkers': bookmarkers,
		'num_bookmarkers': bookmarkers.count(),
		'bookmark_url': bookmark_url,
		'title_text': title_text
    }

