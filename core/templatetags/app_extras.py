import bleach
from core.models import Country
from core.utils import parse_phone_number, is_mobile
from django import template
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
# from django.template.defaultfilters import stringfilter
from django.utils.translation import gettext_lazy as _
from past_papers.mixins import can_edit_comment, can_delete_comment
# I imported the User module directly; this was to ensure that 
# the User methods will be highlighted by the code editor; xD
# just allow it as it is.
from users.models import User

register = template.Library()


register.filter('is_mobile', is_mobile)
register.filter('parse_tel', parse_phone_number)

## register qa_site editing and deleting methods
register.filter(User.can_edit_comment)
register.filter(User.can_delete_comment)
register.filter(User.can_edit_answer)
register.filter(User.can_delete_answer)

## register past_papers editing and deleting methods..
# set a name for the filter so it doesn't clash with the User/qa_site methods
register.filter('can_edit_past_paper_comment', can_edit_comment)
register.filter('can_delete_past_paper_comment', can_delete_comment)


@register.simple_tag
def get_countries():
	return Country.objects.all()


@register.simple_tag(takes_context=True)
def get_default_country(context):
	"""Get default country. """
	# If session.country_code doesn't exist, then return user's country
	country_code = context['request'].session.get('country_code')
	if country_code:
		return Country.objects.get(code=country_code)

	return context['user'].country


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


@register.filter
def opposite_language(lang_code):
	"""
	Returns the 'opposite' of a given language.
	eg. `en` return fr and `fr` returns en
	"""
	return 'en' if lang_code == 'fr' else 'fr'


@register.filter
def should_attribute(object, current_lang):
	"""
	Verify if Google's Google Translate should be attributed.
	We display attribution to Google Translate if:
	- there is an update_language and it is not equal to the current language
	- there is no update_language(use original_language) and the current language 
	is not the original_language
	"""
	original_lang, update_lang = object.original_language, object.update_language

	if update_lang and update_lang != current_lang or \
		not update_lang and original_lang != current_lang:
		return True
	return False


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


@register.simple_tag
def get_login_url():
	login_url = getattr(settings, 'LOGIN_URL', None)
	if not login_url:
		raise ImproperlyConfigured(_('LOGIN_URL is not defined in the settings'))
	if not login_url.endswith('/'):
		login_url += '/'
	return login_url


@register.inclusion_tag('core/bookmarking.html', takes_context=True)
def render_bookmark_template(
	context,
	object, 
	bookmark_url, 
	bookmarks_url,
	title_text=_('Add this post to your favourites. (click again to undo)')
):
	# remember SocialProfile doesn't have 'id' field
	SocialProfile = apps.get_model('socialize.SocialProfile')
	object_model = type(object)

	if object_model == SocialProfile:
		bookmarkers = object.bookmarkers.only('user_id')
	else:
		bookmarkers = object.bookmarkers.only('id')
	
	return {
		'user': context['user'],
		'request': context['request'],
		'object_id': object.user_id if object_model == SocialProfile else object.id,
		'bookmarkers': bookmarkers,
		'num_bookmarkers': bookmarkers.count(),
		# url that contains view that handles bookmark request
		'bookmark_url': bookmark_url,
		# url that maps to view that maps to template where bookmarked posts are
		'bookmarks_url': bookmarks_url,  
		'title_text': title_text
    }

