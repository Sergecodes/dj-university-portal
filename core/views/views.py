from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.http import HttpResponseServerError
from django.http.response import Http404
from django.shortcuts import render, redirect
from django.template import loader
from django.template.context import Context, RequestContext
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_POST
from django.views.generic.base import TemplateView

from core.constants import (
	ANSWER_ACADEMIC_QUESTION_POINTS_CHANGE, ANSWER_CAN_DELETE_VOTE_LIMIT, 
	ANSWER_CAN_EDIT_VOTE_LIMIT, ANSWER_SCHOOL_QUESTION_POINTS_CHANGE, 
	ASK_QUESTION_POINTS_CHANGE, COMMENT_CAN_DELETE_UPVOTE_LIMIT, 
	COMMENT_CAN_EDIT_TIME_LIMIT, COMMENT_CAN_EDIT_UPVOTE_LIMIT, INITIAL_POINTS, 
	MAX_ANSWERS_PER_USER_PER_QUESTION, PAST_PAPER_CAN_DELETE_TIME_LIMIT, 
	PAST_PAPER_COMMENT_CAN_TOUCH_LIMIT, REQUIRED_DOWNVOTE_POINTS, 
	POST_DOWNVOTE_POINTS_CHANGE, POST_UPVOTE_POINTS_CHANGE, 
	QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT, QUESTION_CAN_DELETE_VOTE_LIMIT, 
	QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT, QUESTION_CAN_EDIT_VOTE_LIMIT, 
)
from core.utils import get_search_results, get_label, get_minutes
from lost_or_found.models import LostItem, FoundItem
from marketplace.models import ItemListing, AdListing
from notifications.models import Notification
from past_papers.models import PastPaper
from qa_site.models import (
	AcademicQuestion, DiscussComment, 
	DiscussQuestion, AcademicAnswer
)
from requested_items.models import RequestedItem


class HomePageView(TemplateView):
	template_name = "core/index.html"

	def get_context_data(self, **kwargs):
		NUM_QUESTIONS, NUM_ITEMS = 5, 6
		context, request = super().get_context_data(**kwargs), self.request
		country_code = request.session.get('country_code')

		## questions ##
		academic_questions = AcademicQuestion.objects \
			.prefetch_related(
				Prefetch(
					'answers', 
					queryset=AcademicAnswer.objects.only('id')
				)
			)[:NUM_QUESTIONS]
		discuss_questions = DiscussQuestion.objects \
			.select_related('school') \
			.prefetch_related(
				Prefetch('comments', queryset=DiscussComment.objects.only('id'))
			)

		if country_code:
			discuss_questions = discuss_questions.filter(
				Q(school__isnull=True) | Q(school__country__code=country_code)
			)
		discuss_questions = discuss_questions[:NUM_QUESTIONS]

		## marketplace(items / adverts) ##
		# since city has been "select_related", it must be among the fields in only()
		# ie it should not be deferred
		item_listings = ItemListing.objects \
			.select_related('city__country') \
			.prefetch_related('photos') \
			.defer('description', 'condition_description', 'original_language')
		ad_listings = AdListing.objects \
			.select_related('city__country') \
			.prefetch_related('photos')

		if country_code:
			item_listings = item_listings.filter(city__country__code=country_code)
			ad_listings = ad_listings.filter(
				Q(city__isnull=True) | Q(city__country__code=country_code)
			)

		item_listings = item_listings[:NUM_ITEMS]
		ad_listings = ad_listings[:NUM_ITEMS]

		# get first photo of each listing
		items_first_photos, ads_first_photos = [], []
		for listing in item_listings:
			items_first_photos.append(listing.photos.first())
		
		for listing in ad_listings:
			if listing.photos.exists():
				ads_first_photos.append(listing.photos.first())
			else:
				ads_first_photos.append(None)

		## requested items ##
		requested_items = RequestedItem.objects \
			.select_related('city__country') \
			.prefetch_related('photos') \
			.only('city', 'item_requested', 'posted_datetime', 'slug')

		if country_code:
			requested_items = requested_items.filter(city__country__code=country_code)

		requested_items = requested_items[:NUM_ITEMS]

		# get first photos of each lost_item..
		requested_items_first_photos = []
		for item in requested_items:
			if item.photos.exists():
				requested_items_first_photos.append(item.photos.first())
			else:
				requested_items_first_photos.append(None)

		## lost and found items ##
		lost_items = LostItem.objects \
			.select_related('city__country') \
			.prefetch_related('photos') \
			.only('city', 'item_lost', 'posted_datetime', 'slug')
		found_items = FoundItem.objects \
			.select_related('city__country') \
			.only('city', 'item_found', 'posted_datetime', 'slug')

		if country_code:
			lost_items = lost_items.filter(city__country__code=country_code)
			found_items = found_items.filter(city__country__code=country_code)

		lost_items = lost_items[:NUM_ITEMS]
		found_items = found_items[:NUM_ITEMS]

		# get first photos of each lost_item..
		lost_items_first_photos = []
		for item in lost_items:
			if item.photos.exists():
				lost_items_first_photos.append(item.photos.first())
			else:
				lost_items_first_photos.append(None)

		## past papers ##
		past_papers = PastPaper.objects \
			.select_related('subject', 'country') \
			.only('subject', 'country', 'title', 'level', 'posted_datetime', 'slug')[:NUM_ITEMS]
		
		context['academic_questions'] = academic_questions
		context['discuss_questions'] = discuss_questions
		context['items_and_photos'] = zip(item_listings, items_first_photos)
		context['ads_and_photos'] = zip(ad_listings, ads_first_photos)
		context['requested_items_and_photos'] = zip(requested_items, requested_items_first_photos)
		context['lost_items_and_photos'] = zip(lost_items, lost_items_first_photos)
		context['found_items'] = found_items
		context['past_papers'] = past_papers

		return context

		'''
		# get questions that have more upvotes than downvotes (at least to give visitor good impression..)
		# see stackoverflow.com/a/51701112/ to understand why distinct is required.
		# basically it's required because we use multiple aggregrations with annotate.
		academic_questions = AcademicQuestion.objects.annotate(
			total_votes=Count('upvoters', distinct=True)-Count('downvoters', distinct=True)
		).prefetch_related(
			Prefetch('answers', queryset=AcademicAnswer.objects.all().only('id'))
		).filter(total_votes__gt=0)[:NUM_QUESTIONS]

		discuss_questions = DiscussQuestion.objects.annotate(
			total_votes=Count('upvoters', distinct=True)-Count('downvoters', distinct=True)
		).prefetch_related(
			Prefetch('comments', queryset=DiscussComment.objects.all().only('id'))
		).filter(total_votes__gt=0)[:NUM_QUESTIONS]
		'''


class NotificationsView(LoginRequiredMixin, TemplateView):
	template_name = "core/notifications.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user = self.request.user

		# get reported notifs for moderators
		# if user.is_mod:
		# 	# note that the attribute `target` can't be used for querying;
		# 	# generic relation specs... xD lol
		# 	reported_notifs = user.notifications.filter(
		# 		category=Notification.REPORTED, 
		# 		absolved=False
		# 	)
		# 	context['reported_notifs'] = reported_notifs
			
		general_notifs = user.notifications.filter(category=Notification.GENERAL)
		flags_notifs = user.notifications.filter(category=Notification.FLAG)
		activities_notifs = user.notifications.filter(category=Notification.ACTIVITY)
		# mentions_notifs = user.notifications.filter(category=Notification.MENTION)
		followings_notifs = user.notifications.filter(category=Notification.FOLLOWING)

		context['activities_notifs'] = activities_notifs
		context['followings_notifs'] = followings_notifs

		## For cases where target posts may be included multiple times
		## use a set() so as to have distinct instances.
		# activies (there may be many activities on a single post; 
		# eg likes, dislikes, comments...)
		activities_notifs_targets = set()
		for notif in activities_notifs:
			activities_notifs_targets.add(notif.target)

		# mentions (user can be mentioned many times under the same post)
		# mentions_notifs_targets = set()
		# for notif in mentions_notifs:
		# 	mentions_notifs_targets.add(notif.target)

		# followings (a single post can have multiple activities, 
		# and user will be notified multiple times)
		followings_notifs_targets = set()
		for notif in followings_notifs:
			followings_notifs_targets.add(notif.target)

		# for flags_notifs, the poster of the flagged post may receive multiple notifications
		# regarding the same post, but these notifications(verbs) are unique.

		## determine if each category has any unread notifs
		# unread() returns the unread notifications in the queryset
		context['general_has_unread'] = general_notifs.unread().exists()
		context['flags_has_unread'] = flags_notifs.unread().exists()
		context['activities_has_unread'] = activities_notifs.unread().exists()
		context['followings_has_unread'] = followings_notifs.unread().exists()

		context['general_notifs'] = general_notifs
		context['flags_notifs'] = flags_notifs
		# context['mentions_notifs_targets'] = mentions_notifs_targets
		context['activities_notifs_targets'] = activities_notifs_targets
		context['followings_notifs_targets'] =  followings_notifs_targets
		
		return context


@require_GET
def search_site(request):
	"""
	Perform a search through all apps on the site 
	based on the keywords received from the form.
	"""
	NUM_ITEMS, RESULTS_TEMPLATE = 5, 'core/search_results.html'

	keywords = request.GET.get('keywords', '')
	keyword_list = keywords.split()

	if not keyword_list:
		return render(
			request, 
			RESULTS_TEMPLATE, 
			{'num_results': 0, 'keyword_list': [], 'keywords': ''}
		)

	results, results_count, count = get_search_results(keyword_list)

	return render(request, RESULTS_TEMPLATE, {
		'keyword_list': keyword_list,
		'keywords': keywords,
		'num_results': count,
		'results_count': results_count,
		'academic_questions': results['academic_questions'][:NUM_ITEMS],
		'discuss_questions': results['discuss_questions'][:NUM_ITEMS],
		'item_listings': results['item_listings'][:NUM_ITEMS],
		'ad_listings': results['ad_listings'][:NUM_ITEMS],
		'requested_items': results['requested_items'][:NUM_ITEMS],
		'lost_items': results['lost_items'][:NUM_ITEMS],
		'found_items': results['found_items'][:NUM_ITEMS],
		'past_papers': results['past_papers'][:NUM_ITEMS],
	})


@require_GET
def get_category_search_results(request, category):
	"""
	Display search results of `keywords` in `category` 
	where category is basicaly an app in site.
	"""
	TEMPLATE_NAME = 'core/category_search_results.html'
	RESULTS_PER_PAGE = 3
	CATEGORIES = (
		'academic_questions', 'discuss_questions', 'item_listings',
		'ad_listings', 'requested_items', 'lost_items', 
		'found_items', 'past_papers'
	)
	keywords = request.GET.get('keywords', '')
	keyword_list = keywords.split()
	
	if not keyword_list:
		return render(request, TEMPLATE_NAME, {
			'keyword_list': [],
			'keywords': '',
			'count': 0
		})

	if category not in CATEGORIES:
		raise Http404(_('Invalid category'))

	results, count = get_search_results(keyword_list, category)

	## paginate results
	paginator = Paginator(results, RESULTS_PER_PAGE)
	page_number = request.GET.get('page')
	# if page_number is None, the first page is returned
	page_obj = paginator.get_page(page_number) 

	return render(request, TEMPLATE_NAME, {
		'keyword_list': keyword_list,
		'keywords': keywords,
		'app_label': get_label(category),
		'results': results,
		'count': count,
		'page_obj': page_obj,
		# if more than one page is present, then the results are paginated
		'is_paginated': paginator.num_pages > 1
	})


def set_session_country(request, country_code=None):
	# Store user's selected country in session 
	if country_code:
		request.session['country_code'] = country_code
	else:
		# pop raises KeyError if key isn't found and no default is specified
		# so specify default as None
		request.session.pop('country_code', None)

	if next_url := request.GET.get('next'):
		return redirect(next_url)
	
	return redirect('/')


class SiteUsageInfoView(TemplateView):
	template_name = "core/site_usage_info.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		# points rewarded when user posts something
		context['post_points'] = 5
		context['new_user_points'] = INITIAL_POINTS
		context['ask_qstn_points'] = ASK_QUESTION_POINTS_CHANGE
		context['upvote_points'] = POST_UPVOTE_POINTS_CHANGE
		context['downvote_points'] = abs(POST_DOWNVOTE_POINTS_CHANGE)
		context['downvote_req_points'] = REQUIRED_DOWNVOTE_POINTS
		context['aca_ans_points'] = ANSWER_ACADEMIC_QUESTION_POINTS_CHANGE
		context['school_ans_points'] = ANSWER_SCHOOL_QUESTION_POINTS_CHANGE
		context['max_answers'] = MAX_ANSWERS_PER_USER_PER_QUESTION
		context['cannot_del_paper_time'] = get_minutes(PAST_PAPER_CAN_DELETE_TIME_LIMIT)
		context['cannot_touch_paper_comment_time'] = get_minutes(PAST_PAPER_COMMENT_CAN_TOUCH_LIMIT)
		context['cannot_edit_qstn_vote'] = QUESTION_CAN_EDIT_VOTE_LIMIT
		context['cannot_edit_qstn_ans_count'] = QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT
		context['cannot_edit_ans_vote'] = ANSWER_CAN_EDIT_VOTE_LIMIT
		context['cannot_edit_comment_vote'] = COMMENT_CAN_EDIT_UPVOTE_LIMIT
		context['cannot_edit_comment_time'] = get_minutes(COMMENT_CAN_EDIT_TIME_LIMIT)
		context['cannot_del_comment_vote'] = COMMENT_CAN_DELETE_UPVOTE_LIMIT
		context['cannot_del_qstn_vote'] = QUESTION_CAN_DELETE_VOTE_LIMIT
		context['cannot_del_qstn_ans_count'] = QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT
		context['cannot_del_ans_vote'] = ANSWER_CAN_DELETE_VOTE_LIMIT
		
		return context


class PrivacyPolicyView(TemplateView):
	template_name = "core/privacy_policy.html"


class TermsAndConditionsView(TemplateView):
	template_name = "core/terms_and_conditions.html"


# def delete_post_and_penalize_user(request):
# 	"""mod only"""
	# delete post and penalize user
# 	# call User.objects.penalize_user(...)
# 	# and 

# def absolve_post...
	# pass


## CUSTOM ERROR HANDLER VIEWS
# def page_not_found_view(request, exception):
# 	return render(request, 'core/error_templates/404.html', {'exception': exception}, status=404)


def server_error_view(request):
	return render(
		request, 
		'500.html', 
		{'url': request.build_absolute_uri()}, 
		status=500
	)
	

# def permission_denied_view(request, exception):
# 	return render(request, 'core/error_templates/403.html', {'exception': exception}, status=403)


# def bad_request_view(request, exception):
# 	return render(request, 'core/error_templates/400.html', {'exception': exception}, status=400)


