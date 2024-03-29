from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.forms import model_to_dict
from django.http import JsonResponse 
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.views.generic import ListView

from notifications import settings
from notifications.models import Notification
from notifications.settings import get_config


class NotificationViewList(ListView):
	template_name = 'notifications/list.html'
	context_object_name = 'notifications'
	paginate_by = settings.get_config()['PAGINATE_BY']

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(NotificationViewList, self).dispatch(
			request, *args, **kwargs)


class AllNotificationsList(NotificationViewList):
	"""
	Index page for authenticated user
	"""

	def get_queryset(self):
		if settings.get_config()['SOFT_DELETE']:
			qset = self.request.user.notifications.active()
		else:
			qset = self.request.user.notifications.all()
		return qset


class UnreadNotificationsList(NotificationViewList):

	def get_queryset(self):
		return self.request.user.notifications.unread()


## added
@login_required	
@require_POST
def mark_post_notifs_as_read(request):
	category, obj_id = request.POST['category'], request.POST['obj_id']
	app_name, model_name = request.POST['app_name'], request.POST['model_name']
	model = apps.get_model(app_name, model_name)

	post_category_notifs = request.user.notifications.filter(
		target_object_id=obj_id,
		target_content_type=ContentType.objects.get_for_model(model),
		category=category  # mark as read only in a given category.
	)
	post_category_notifs.mark_all_as_read()
	
	if next_url := request.POST.get('next'):
		return redirect(next_url)

	return redirect('notifications:unread')


@login_required
@require_POST
def mark_all_post_notifs_as_read(request):
	category_notifs = request.user.notifications.filter(
		category=request.POST['category']  
	)
	category_notifs.mark_all_as_read()
	
	if next_url := request.POST.get('next'):
		return redirect(next_url)
		
	return redirect('notifications:unread')


## added
@login_required	
@require_POST
def delete_post_notifs(request):
	category, obj_id = request.POST['category'], request.POST['obj_id']
	app_name, model_name = request.POST['app_name'], request.POST['model_name']
	model = apps.get_model(app_name, model_name)

	post_category_notifs = request.user.notifications.filter(
		target_object_id=obj_id,
		target_content_type=ContentType.objects.get_for_model(model),
		category=category
	)
	post_category_notifs.delete()
	
	if next_url := request.POST.get('next'):
		return redirect(next_url)
		
	return redirect('notifications:unread')


## added
@login_required	
@require_POST
def delete_all_post_notifs(request):
	category_notifs = request.user.notifications.filter(
		category=request.POST['category']
	)
	category_notifs.delete()
	
	if next_url := request.POST.get('next'):
		return redirect(next_url)
		
	return redirect('notifications:unread')


## added
@login_required
@require_POST
def mark_category_as_read(request):
	category = request.POST['category']
	request.user.notifications.filter(category=category).mark_all_as_read()

	if next_url := request.POST.get('next'):
		return redirect(next_url)
		
	return redirect('notifications:unread')


## added
@login_required
@require_POST
def delete_category_notifs(request):
	category = request.POST['category']
	request.user.notifications.filter(category=category).delete()

	if next_url := request.POST.get('next'):
		return redirect(next_url)
		
	return redirect('notifications:unread')


@login_required
@require_POST
def mark_all_as_read(request):
	request.user.notifications.mark_all_as_read()
	
	if next_url := request.POST.get('next'):
		return redirect(next_url)
		
	return redirect('notifications:unread')


@login_required
@require_POST
def mark_as_read(request):
	notif_id = request.POST['notif_id']
	notification = get_object_or_404(Notification, recipient=request.user, id=notif_id)
	notification.mark_as_read()

	if next_url := request.POST.get('next'):
		return redirect(next_url)

	return redirect('notifications:unread')


@login_required
@require_POST
def mark_as_unread(request):
	notif_id = request.POST['notif_id']
	notification = get_object_or_404(Notification, recipient=request.user, id=notif_id)
	notification.mark_as_unread()

	if next_url := request.POST.get('next'):
		return redirect(next_url)

	return redirect('notifications:unread')


@login_required
@require_POST
def delete(request):
	notif_id = request.POST['notif_id']
	notification = get_object_or_404(Notification, recipient=request.user, id=notif_id)

	if settings.get_config()['SOFT_DELETE']:
		notification.deleted = True
		notification.save()
	else:
		notification.delete()

	if next_url := request.POST.get('next'):
		return redirect(next_url)

	return redirect('notifications:all')


@never_cache
def live_unread_notification_count(request):
	user_is_authenticated = request.user.is_authenticated

	if not user_is_authenticated:
		data = {
			'unread_count': 0
		}
	else:
		data = {
			'unread_count': request.user.notifications.unread().count(),
		}
	return JsonResponse(data)


@never_cache
def live_unread_notification_list(request):
	''' Return a json with a unread notification list '''
	user_is_authenticated = request.user.is_authenticated

	if not user_is_authenticated:
		data = {
			'unread_count': 0,
			'unread_list': []
		}
		return JsonResponse(data)

	default_num_to_fetch = get_config()['NUM_TO_FETCH']
	try:
		# If they don't specify, make it 5.
		num_to_fetch = request.GET.get('max', default_num_to_fetch)
		num_to_fetch = int(num_to_fetch)
		if not (1 <= num_to_fetch <= 100):
			num_to_fetch = default_num_to_fetch
	except ValueError:  # If casting to an int fails.
		num_to_fetch = default_num_to_fetch

	unread_list = []

	for notification in request.user.notifications.unread()[0:num_to_fetch]:
		struct = model_to_dict(notification)
		struct['slug'] = notification.id
		if notification.actor:
			struct['actor'] = str(notification.actor)
		if notification.target:
			struct['target'] = str(notification.target)
		if notification.action_object:
			struct['action_object'] = str(notification.action_object)
		if notification.data:
			struct['data'] = notification.data
		unread_list.append(struct)
		if request.GET.get('mark_as_read'):
			notification.mark_as_read()
	data = {
		'unread_count': request.user.notifications.unread().count(),
		'unread_list': unread_list
	}
	return JsonResponse(data)


@never_cache
def live_all_notification_list(request):
	''' Return a json with a unread notification list '''
	user_is_authenticated = request.user.is_authenticated

	if not user_is_authenticated:
		data = {
			'all_count': 0,
			'all_list': []
		}
		return JsonResponse(data)

	default_num_to_fetch = get_config()['NUM_TO_FETCH']
	try:
		# If they don't specify, make it 5.
		num_to_fetch = request.GET.get('max', default_num_to_fetch)
		num_to_fetch = int(num_to_fetch)
		if not (1 <= num_to_fetch <= 100):
			num_to_fetch = default_num_to_fetch
	except ValueError:  # If casting to an int fails.
		num_to_fetch = default_num_to_fetch

	all_list = []

	for notification in request.user.notifications.all()[0:num_to_fetch]:
		struct = model_to_dict(notification)
		struct['slug'] = notification.id
		if notification.actor:
			struct['actor'] = str(notification.actor)
		if notification.target:
			struct['target'] = str(notification.target)
		if notification.action_object:
			struct['action_object'] = str(notification.action_object)
		if notification.data:
			struct['data'] = notification.data
		all_list.append(struct)
		if request.GET.get('mark_as_read'):
			notification.mark_as_read()
	data = {
		'all_count': request.user.notifications.count(),
		'all_list': all_list
	}
	return JsonResponse(data)


def live_all_notification_count(request):
	user_is_authenticated = request.user.is_authenticated

	if not user_is_authenticated:
		data = {
			'all_count': 0
		}
	else:
		data = {
			'all_count': request.user.notifications.count(),
		}
	return JsonResponse(data)
