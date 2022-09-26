"""Basically for views that return a JsonResponse"""
import json
import mimetypes
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.db.models import F
from django.db.models.query import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import get_language, gettext_lazy as _
from django.views import View
from django.views.decorators.http import require_POST, require_GET, require_http_methods

from core.constants import (
	POST_UPVOTE_POINTS_CHANGE, POST_DOWNVOTE_POINTS_CHANGE,
	THRESHOLD_POINTS, COMMENT_CAN_EDIT_VOTE_LIMIT, ACADEMIC_COMMENTS_PHOTOS_UPLOAD_DIR,
	COMMENT_CAN_DELETE_VOTE_LIMIT, DISCUSS_COMMENTS_PHOTOS_UPLOAD_DIR
)
from flagging.models import Flag
from notifications.models import Notification
from notifications.signals import notify
from ..forms import (
	DiscussCommentForm, DiscussCommentPhotoForm,
	AcademicCommentForm, AcademicCommentPhotoForm
)
from ..models import (
	DiscussQuestion, AcademicQuestion, DiscussComment, AcademicComment,
	DiscussCommentPhoto, AcademicCommentPhoto
)

User = get_user_model()


def _parse_jquery_comment(current_user, comment):
	"""Parse comment for appropriately using in jquery-comments"""
	poster, user = comment.poster, current_user
	obj = {
		'id': comment.id,
		'parent': comment.parent_id,
		'created': comment.posted_datetime,
		'modified': comment.last_modified,
		'content': comment.content,
		'creator': poster.id,
		'fullname': poster.username,
		'created_by_admin': False,
		'created_by_current_user': user.id == poster.id,
		'upvote_count': comment.upvote_count,
		'user_has_upvoted': False if user.is_anonymous else user in comment.upvoters.only('id'),
		'is_new': False,
		# extra
		'has_flagged': False if user.is_anonymous else Flag.objects.has_flagged(user, comment),
	}

	# Add downvote_count for academic comment
	if isinstance(comment, AcademicComment):
		obj['downvote_count'] = comment.downvote_count
		obj['user_has_downvoted'] = False if user.is_anonymous else user in comment.downvoters.only('id')

	try:
		obj['profile_picture_url'] = poster.social_profile.profile_image.url
	except (AttributeError, ValueError):
		# AttributeError in case user has no social_profile(hence None)
		# ValueError in case profile_image has no url(no file associated) 
		obj['profile_picture_url'] = ''

	pings = {}
	for user in comment.users_mentioned.only('id', 'username').all():
		pings[user.id] = user.username

	# pings should be an empty array if no ping is present else
	# it should be an object of pings
	obj['pings'] = [] if len(pings) == 0 else pings

	## Add attachments
	attachments = []
	for photo in comment.photos.all():
		attachments.append({
			'id': photo.id,
			'file': photo.file.url,
			'mime_type': mimetypes.guess_type(photo.file.name)[0]
		})
	obj['attachments'] = attachments

	return obj


@method_decorator(login_required, name='post')
class JQueryCommentList(View):
	"""
	In all request, `model_name` refers to the name of the comment model.
	It should be AcademicComment or DiscussComment.
	"""
	def get(self, request, model_name):
		"""
		Get discuss/academic comments to display in frontend (using jquery-comments).
		see https://viima.github.io/jquery-comments/.
		`model_name` can be AcademicComment | DiscussComment
		"""
		all_users = User.objects.active()
		comment_model = apps.get_model('qa_site', model_name)

		comments = comment_model.objects \
			.select_related('parent', 'poster__social_profile') \
			.prefetch_related(
				Prefetch('users_mentioned', queryset=all_users.only('id', 'username')),
				Prefetch('upvoters', queryset=all_users.only('id'))
			) \
			.all()

		result = [_parse_jquery_comment(request.user, comment) for comment in comments]
		return JsonResponse({ 'data': result })

	def post(self, request, model_name):
		# When posting, send content, question_id & optional parent_id
		comment_model = apps.get_model('qa_site', model_name)

		if model_name == 'AcademicComment':
			qstn_model = AcademicQuestion
			photo_model = AcademicCommentPhoto
			photo_form_class = AcademicCommentPhotoForm
		else:
			qstn_model = DiscussQuestion
			photo_model = DiscussCommentPhoto
			photo_form_class = DiscussCommentPhotoForm

		POST, user = request.POST, request.user
		form = DiscussCommentForm(POST) if model_name == 'DiscussComment' else AcademicCommentForm(POST)
		if not form.is_valid():
			return JsonResponse({ 
				'data': form.errors.as_json(),
				'type': 'comment'
			}, status=400)

		files = request.FILES.getlist('attachments')
		if files:
			photo_form = photo_form_class(request.POST, request.FILES)
			if not photo_form.is_valid():
				return JsonResponse({ 
					'data': photo_form.errors.as_json(),
					'type': 'photo'
				}, status=400)

		parent_id = POST.get('parent_id')
		question = get_object_or_404(qstn_model, pk=POST['question_id'])
		parent = get_object_or_404(comment_model, pk=parent_id) if parent_id else None

		comment = form.save(commit=False)
		user.add_question_comment(question, comment, parent)

		# Set pinged users
		if pingedIds := POST['pingedIds']:
			comment.users_mentioned.add(*pingedIds)

		# Add files
		if files:
			photos = [photo_model(file=f, comment=comment) for f in files]
			photo_model.objects.bulk_create(photos)

		return JsonResponse({ 'data': _parse_jquery_comment(user, comment) }, status=201)


@method_decorator(login_required, name='put')
@method_decorator(login_required, name='delete')
class JQueryCommentDetail(View):
	def get(self, request, model_name, id):
		comment_model = apps.get_model('qa_site', model_name)
		comment = get_object_or_404(comment_model, pk=id)
		return JsonResponse({ 'data': _parse_jquery_comment(request.user, comment) })

	def put(self, request, model_name, id, data):
		print('data', data)
		
		# see https://stackoverflow.com/a/42513184 (handle file upload via put request)
		if request.content_type.startswith('multipart'):
			put, files = request.parse_file_upload(request.META, request)
			request.FILES.update(files)
			
		if model_name == 'AcademicComment':
			photo_model = AcademicCommentPhoto
			photo_form_class = AcademicCommentPhotoForm
		else:
			photo_model = DiscussCommentPhoto
			photo_form_class = DiscussCommentPhotoForm

		request.PUT, files = json.loads(data), request.FILES.getlist('attachments')
		if files:
			photo_form = photo_form_class(request.PUT, request.FILES)
			if not photo_form.is_valid():
				return JsonResponse({ 
					'data': photo_form.errors.as_json(),
					'type': 'photo'
				}, status=400)

		PUT, user = request.PUT, request.user
		content, success = PUT['content'], True
		comment_model = apps.get_model('qa_site', model_name)
		comment = get_object_or_404(comment_model, pk=id)	

		if not user.can_edit_comment(comment):
			success = False

			if user.id == comment.poster_id:
				message = _(
					"Comments that have more than a score of {} cannot be edited"
						.format(COMMENT_CAN_EDIT_VOTE_LIMIT)
				)
			else:
				message = _("You are not permitted to edit this comment")

		if success == False:
			return JsonResponse({
				'success': False,
				'message': message
			}, status=403)

		if len(files) == 0 and content == comment.content:
			return JsonResponse({
				'success': False,
				'message': _("This comment's content hasn't changed")
			}, status=400)

		current_lang = get_language()
		comment.content = content
		comment.update_language = current_lang
		# Without this, the content isn't updated in the current language
		setattr(comment, f'content_{current_lang}', content)
		comment.save(update_fields=[
			'content', 'update_language', f'content_{current_lang}', 'last_modified'
		])
		comment.users_mentioned.set(PUT['pingedIds'], clear=True)
		print(comment.users_mentioned.all())

		if files:
			photos = [photo_model(file=f, comment=comment) for f in files]
			photo_model.objects.bulk_create(photos)

		return JsonResponse({ 'data': _parse_jquery_comment(user, comment) })

	def delete(self, request, model_name, id):
		user, success = request.user, True
		comment_model = apps.get_model('qa_site', model_name)
		comment = get_object_or_404(comment_model, pk=id)

		if comment.parent_id is None:
			if not user.can_delete_comment(comment):
				success = False

				if user.id == comment.poster_id:
					message = _(
						"Comments that have more than {} likes cannot be deleteed"
							.format(COMMENT_CAN_DELETE_VOTE_LIMIT)
					)
				else:
					message = _("You are not permitted to delete this comment")
		else:
			if not user.can_delete_comment(comment):
				success = False

				if user.id == comment.poster_id:
					message = _(
						"Replies that have more than {} likes cannot be DELETED" \
						.format(COMMENT_CAN_DELETE_VOTE_LIMIT)
					)
				else:
					message = _('You are not permitted to DELETE this comment')

		if success == False:
			return JsonResponse({
				'success': False,
				'message': message
			}, status=403)

		comment.delete()
		return JsonResponse({ 'success': True }, status=204)


@require_http_methods(["DELETE"])
def delete_comment_attachment(request, model_name, id, filename):
	if model_name == 'AcademicComment':
		photo_model = AcademicCommentPhoto
		upload_path = ACADEMIC_COMMENTS_PHOTOS_UPLOAD_DIR
	else:
		photo_model = DiscussCommentPhoto
		upload_path = DISCUSS_COMMENTS_PHOTOS_UPLOAD_DIR

	photo = get_object_or_404(photo_model, comment=id, file=upload_path + filename)
	photo.delete()
	return JsonResponse({ 'success': True }, status=204)


@require_GET
def get_users_mentioned(request, question_id):
	"""Get all users mentioned in academic or discuss question post"""
	model_name = request.GET['model_name']
	try:
		for_jquery = bool(int(request.GET.get('for_jquery', 0)))
	except TypeError:
		for_jquery = False

	# if model_name not in ['AcademicComment', 'DiscussComment']:
	# 	return JsonResponse({
	# 		'success': False,
	# 		'message': _('Invalid model type')
	# 	}, status=400)

	comment_model = apps.get_model('qa_site', model_name)
	qstn_model = DiscussQuestion if model_name == 'DiscussComment' else AcademicQuestion
	question = get_object_or_404(qstn_model, pk=question_id)

	qstns = qstn_model.objects.prefetch_related(
		Prefetch('comments', comment_model.objects.only('id', 'users_mentioned'))
	)
	users = User.objects.filter(id=question.poster_id)

	for question in qstns:
		for comment in question.comments.all():
			if for_jquery:
				users |= comment.users_mentioned.select_related('social_profile').all()
			else:
				users |= comment.users_mentioned.all()

	if not for_jquery:
		result = list(users.distinct().values())
	else:
		result = []
		for user in users.distinct():
			start_url = request.scheme + '://' + get_current_site(request).domain
			obj = {
				'id': user.id,
				'fullname': user.username,
				'email': user.email,
				# extra
				'social_profile_url': start_url + user.social_profile.get_absolute_url() if user.has_social_profile else ''
			}
			try:
				obj['profile_picture_url'] = user.social_profile.profile_image.url
			except (AttributeError, ValueError):
				obj['profile_picture_url'] = ''

			result.append(obj)

	return JsonResponse({ 'data': result })


@login_required
@require_POST
def vote_academic_thread(request):
	"""
	This view handles upvotes and downvotes for questions, answers and comments of an academic question.
	It should be called via client side..
	"""
	user, POST = request.user, request.POST
	thread_id, thread_type = POST.get('id'), POST.get('thread_type')
	vote_action, vote_type = POST.get('action'), POST.get('vote_type')
	# print(POST)
	
	# possible thread types are {question, comment}
	if thread_type == 'question':
		object = get_object_or_404(AcademicQuestion, pk=thread_id)
	elif thread_type == 'comment':
		object = get_object_or_404(AcademicComment, pk=thread_id)
	else:
		return JsonResponse({
			'success': False,
			'message': _('Invalid thread type')
		}, status=400)

	thread_owner = object.poster

	# user can't vote for his own post
	# this should normally be prevented in frontend 
	if user == thread_owner:
		return JsonResponse({
			'success': False,
			'message': _("You can't add a like or dislike to your own post.")
		}, status=403)

	if thread_type == 'question':
		# if vote is new (not retracting a previous vote)
		# in frontend, voters won't be displayed.
		if vote_action == 'vote':
			if vote_type == 'up':
				with transaction.atomic():
					object.downvoters.remove(user)
					object.upvoters.add(user)

					# update points of post owner
					thread_owner.site_points = F('site_points') + POST_UPVOTE_POINTS_CHANGE
					thread_owner.save(update_fields=['site_points'])

				# send notification to post owner
				notify.send(
					sender=user, 
					recipient=thread_owner, 
					verb=_('liked your question') if thread_type == 'question' else _('liked your answer'),
					target=object,
					category=Notification.ACTIVITY
				)
				return JsonResponse({
					'success': True,
					'message': _('Added like')
				}, status=200)

			elif vote_type == 'down':
				with transaction.atomic():
					object.upvoters.remove(user)
					downvote_result = user.downvote_question(object, for_html=True)

					# update points of post owner
					thread_owner.site_points = F('site_points') + POST_DOWNVOTE_POINTS_CHANGE
					thread_owner.save(update_fields=['site_points'])

				if not downvote_result[0]:
					return JsonResponse({
						'success': False,
						'message': downvote_result[1]
					}, status=400)

				# send notification to post owner
				notify.send(
					sender=user, 
					recipient=thread_owner, 
					verb=_('disliked your question') if thread_type == 'question' else _('disliked your answer'),
					target=object,
					category=Notification.ACTIVITY
				)
				return JsonResponse({
					'success': True,
					'message': _('Added dislike')
				}, status=200)

			else:
				return JsonResponse({
					'success': False,
					'message': _('Unknown vote type')
				}, status=400)

		# if user is retracting a vote
		# no notification sent
		elif vote_action == 'recall-vote':
			if vote_type == 'up':
				with transaction.atomic():
					object.upvoters.remove(user)

					# update points of post owner
					# subtract points since vote is being retracted
					thread_owner.site_points = F('site_points') - POST_UPVOTE_POINTS_CHANGE
					thread_owner.save(update_fields=['site_points'])

				return JsonResponse({
					'success': True,
					'message': _('Removed like')
				}, status=200)

			elif vote_type == 'down':
				with transaction.atomic():
					object.downvoters.remove(user)

					# update points of post owner
					# add points since vote is being retracted
					user_points = thread_owner.site_points
					# see core.constants.py file; `RESTRICTED_POINTS` comment for explanation
					if user_points != THRESHOLD_POINTS:
						thread_owner.site_points = F('site_points') - POST_DOWNVOTE_POINTS_CHANGE
						thread_owner.save(update_fields=['site_points'])

				return JsonResponse({
					'success': True,
					'message': _('Removed dislike')
				}, status=200)
			else:
				return JsonResponse({
					'success': False,
					'message': _('Unknown vote type')
				}, status=400)
		# invalid action (action must be in {'vote', 'recall-vote'})
		else:
			return JsonResponse({
				'success': False,
				'message': _('Bad action')
			}, status=400)
	
	elif thread_type == 'comment':
		# if user is adding new vote
		if vote_action == 'vote':
			if vote_type == 'up':
				with transaction.atomic():
					object.downvoters.remove(user)
					object.upvoters.add(user)

				return JsonResponse({
					'success': True,
					'message': _('Added like')
				}, status=200)

			elif vote_type == 'down':
				with transaction.atomic():
					object.upvoters.remove(user)
					downvote_result = user.downvote_comment(object, for_html=True)

				if not downvote_result[0]:
					return JsonResponse({
						'success': False,
						'message': downvote_result[1]
					}, status=400)

				return JsonResponse({
					'success': True,
					'message': _('Added dislike')
				}, status=200)

			else:
				return JsonResponse({
					'success': False,
					'message': _('Unknown vote type')
				}, status=400)
			
		# if user is retracting vote
		elif vote_action == 'recall-vote':
			if vote_type == 'up':
				object.upvoters.remove(user)
				return JsonResponse({
					'success': True,
					'message': _('Removed like')
				}, status=200)

			elif vote_type == 'down':
				object.downvoters.remove(user)
				return JsonResponse({
					'success': True,
					'message': _('Removed dislike')
				}, status=200)

			else:
				return JsonResponse({
					'success': False,
					'message': _('Unknown vote type')
				}, status=400)
		# invalid action(action should either be 'vote' or 'recall-vote')
		else:
			return JsonResponse({
				'success': False,
				'message': _('Bad action')
			}, status=400)


@login_required
@require_POST
def vote_discuss_thread(request):
	"""
	This view handles upvotes and downvotes for questions, answers and comments of discussion questions.
	"""
	user, POST = request.user, request.POST
	thread_id, thread_type = POST['id'], POST['thread_type']
	vote_action, vote_type = POST['action'], POST['vote_type']

	# possible thread types are {question, comment}
	if thread_type == 'question':
		object = get_object_or_404(DiscussQuestion, pk=thread_id)
	elif thread_type == 'comment':
		object = get_object_or_404(DiscussComment, pk=thread_id)
	else:
		return JsonResponse({
			'success': False,
			'message': _('Invalid thread type')
		}, status=400)

	thread_owner = object.poster

	# user can't vote for his own post
	# this should normally be prevented in frontend 
	if user == thread_owner:
		return JsonResponse({
			'success': False,
			'message': _("You can't add a like or dislike to your own post.")
		}, status=403)

	if thread_type == 'question':
		# if vote is new (not retracting a previous vote)
		if vote_action == 'vote':
			if vote_type == 'up':
				with transaction.atomic():
					object.downvoters.remove(user)
					object.upvoters.add(user)

					# update points of post owner
					thread_owner.site_points = F('site_points') + POST_UPVOTE_POINTS_CHANGE
					thread_owner.save(update_fields=['site_points'])

				# send notification to post owner
				notify.send(
					sender=user,
					recipient=thread_owner, 
					verb=_('liked your question') if thread_type == 'question' else _('liked your answer'),
					target=object,
					category=Notification.ACTIVITY
				)
				return JsonResponse({
						'success': True,
						'message': _('Added like')
					}, status=200)

			elif vote_type == 'down':
				with transaction.atomic():
					object.upvoters.remove(user)
					downvote_result = user.downvote_question(object, for_html=True)

					# update points of post owner
					thread_owner.site_points = F('site_points') + POST_DOWNVOTE_POINTS_CHANGE
					thread_owner.save(update_fields=['site_points'])

				if not downvote_result[0]:
					return JsonResponse({
						'success': False,
						'message': downvote_result[1]
					}, status=400)

				# send notification to post owner
				notify.send(
					sender=user, 
					recipient=thread_owner, 
					verb=_('disliked your question') if thread_type == 'question' else _('disliked your answer'),
					target=object,
					category=Notification.ACTIVITY
				)
				return JsonResponse({
					'success': True,
					'message': _('Added dislike')
				}, status=200)

			else:
				return JsonResponse({
					'success': False,
					'message': _('Unknown vote type')
				}, status=400)

		# if user is retracting a vote
		elif vote_action == 'recall-vote':
			if vote_type == 'up':
				with transaction.atomic():
					object.upvoters.remove(user)

					# update points of post owner
					# subtract points since vote is being retracted
					thread_owner.site_points = F('site_points') - POST_UPVOTE_POINTS_CHANGE
					thread_owner.save(update_fields=['site_points'])

				return JsonResponse({
						'success': True,
						'message': _('Removed like')
					}, status=200)

			elif vote_type == 'down':
				with transaction.atomic():
					object.downvoters.remove(user)

					# update points of post owner
					# add points back since vote is being retracted
					user_points = thread_owner.site_points
					# see core.constants.py file; `RESTRICTED_POINTS` comment for explanation
					if user_points != THRESHOLD_POINTS:
						thread_owner.site_points = F('site_points') - POST_DOWNVOTE_POINTS_CHANGE
						thread_owner.save(update_fields=['site_points'])

				return JsonResponse({
						'success': True,
						'message': _('Removed dislike')
					}, status=200)
			else:
				return JsonResponse({
						'success': False,
						'message': _('Unknown vote type')
					}, status=400)
		else:
			return JsonResponse({
				'success': False,
				'message': _('Bad action')
			}, status=400)
	
	# only upvotes are supported on comments
	# no notifications sent to owner of comment
	# 
	# Only comment for discusions
	elif thread_type == 'comment':
		already_upvoted = user in object.upvoters.only('id')

		if vote_action == 'vote':
			if not already_upvoted:
				if vote_type == 'up':
					object.upvoters.add(user)
					return JsonResponse({
						'success': True,
						'message': _('Added like')
					}, status=200)
				else:
					return JsonResponse({
						'success': False,
						'message': _('Unknown vote type')
					}, status=400)
			# if user has already_voted but sends 'vote' as the vote_action
			else:
				return JsonResponse({
					'success': False,
					'message': _('Bad action, already voted. Use `recall-vote` as the vote_action.')
				}, status=400)

		elif vote_action == 'recall-vote':
			if vote_type == 'up' and already_upvoted:
				object.upvoters.remove(user)
				return JsonResponse({
					'success': True,
					'message': _('Removed like')
				}, status=200)
			else:
				return JsonResponse({
						'success': False,
						'message': _('Unknown vote type or no vote to recall')
					}, status=400)
		else:
			return JsonResponse({
				'success': False,
				'message': _('Bad action')
			}, status=400)


@login_required
@require_POST
def academic_question_bookmark_toggle(request):
	"""This view handles bookmarking for academic questions"""
	# yes, user can bookmark his own question
	user, POST = request.user, request.POST
	id, action = POST.get('id'), POST.get('action')
	question = get_object_or_404(AcademicQuestion, pk=id)

	# if vote is new (not removing bookmark)
	if action == 'bookmark':
		question.bookmarkers.add(user)
		return JsonResponse({'bookmarked': True}, status=200)

	# if user is retracting bookmark
	elif action == 'recall-bookmark':
		question.bookmarkers.remove(user)
		return JsonResponse({'unbookmarked': True}, status=200)
	else:
		return JsonResponse({'error': _('Invalid action')}, status=400)


@login_required
@require_POST
def discuss_question_bookmark_toggle(request):
	"""This view handles bookmarking for discussion questions"""
	user, POST = request.user, request.POST
	id, action = POST.get('id'), POST.get('action')
	question = get_object_or_404(DiscussQuestion, pk=id)

	# if vote is new (not removing bookmark)
	if action == 'bookmark':
		question.bookmarkers.add(user)
		return JsonResponse({'bookmarked': True}, status=200)

	# if user is retracting bookmark
	elif action == 'recall-bookmark':
		question.bookmarkers.remove(user)
		return JsonResponse({'unbookmarked': True}, status=200)
	else:
		return JsonResponse({'error': _('Invalid action')}, status=400)


@login_required
@require_POST
def academic_question_follow_toggle(request):
	"""This view handles following for academic questions"""
	user, POST = request.user, request.POST
	id, action = POST.get('id'), POST.get('action')
	question = get_object_or_404(AcademicQuestion, pk=id)

	# user can't follow his own question
	if user.id == question.poster_id:
		return JsonResponse({'error': _("You can't follow your own question")}, status=403)

	# if user is following
	if action == 'follow':
		question.followers.add(user)
		return JsonResponse({'followed': True}, status=200)

	# if user is unfollowing
	elif action == 'recall-follow':
		question.followers.remove(user)
		return JsonResponse({'unfollowed': True}, status=200)
	else:
		return JsonResponse({'error': _('Invalid action')}, status=400)


@login_required
@require_POST
def discuss_question_follow_toggle(request):
	"""This view handles following for discussion questions"""
	user, POST = request.user, request.POST
	id, action = POST.get('id'), POST.get('action')
	question = get_object_or_404(DiscussQuestion, pk=id)

	# user can't follow his own question
	if user.id == question.poster_id:
		return JsonResponse({'message': _("You can't follow your own question")}, status=403)

	# if user is following
	if action == 'follow':
		question.followers.add(user)
		return JsonResponse({'success': True}, status=200)

	# if user is unfollowing
	elif action == 'recall-follow':
		question.followers.remove(user)
		return JsonResponse({'success': True}, status=200)
	else:
		return JsonResponse({'message': _('Invalid action')}, status=400)


