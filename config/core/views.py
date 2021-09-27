from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.views.generic.base import TemplateView

from core.models import Notification
from lost_and_found.models import LostItem, FoundItem
from marketplace.models import ItemListing, AdListing
from past_papers.models import PastPaper
from qa_site.models import (
	AcademicQuestion, SchoolQuestion,
	AcademicAnswer, SchoolAnswer
)
from requested_items.models import RequestedItem


class HomePageView(TemplateView):
	template_name = "core/index.html"

	def get_context_data(self, **kwargs):
		NUM_QUESTIONS, NUM_ITEMS = 3, 6
		context = super().get_context_data(**kwargs)

		## questions ##
		academic_questions = AcademicQuestion.objects.prefetch_related(
			Prefetch('answers', queryset=AcademicAnswer.objects.all().only('id'))
		).defer('content')[:NUM_QUESTIONS]
		school_questions = SchoolQuestion.objects.select_related('school').prefetch_related(
			Prefetch('answers', queryset=SchoolAnswer.objects.all().only('id'))
		)[:NUM_QUESTIONS]

		## marketplace(items / adverts) ##
		# since school has been "select_related", it must be among the fields in only()
		item_listings = ItemListing.objects.select_related('school').prefetch_related(
			'photos'
		).defer('description', 'condition_description', 'original_language')[:NUM_ITEMS]
		ad_listings = AdListing.objects.select_related('school').prefetch_related(
			'photos'
		)[:NUM_ITEMS]

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
		requested_items = RequestedItem.objects.select_related('school').prefetch_related('photos').only(
			'school', 'item_requested', 'posted_datetime', 'slug'
		)[:NUM_ITEMS]

		# get first photos of each lost_item..
		requested_items_first_photos = []
		for item in requested_items:
			if item.photos.exists():
				requested_items_first_photos.append(item.photos.first())
			else:
				requested_items_first_photos.append(None)

		## lost and found items ##
		lost_items = LostItem.objects.select_related('school').prefetch_related('photos').only(
			'school', 'item_lost', 'posted_datetime', 'slug'
		)[:NUM_ITEMS]
		found_items = FoundItem.objects.select_related('school').only(
			'school', 'item_found', 'posted_datetime', 'slug'
		)[:NUM_ITEMS]

		# get first photos of each lost_item..
		lost_items_first_photos = []
		for item in lost_items:
			if item.photos.exists():
				lost_items_first_photos.append(item.photos.first())
			else:
				lost_items_first_photos.append(None)

		## past papers ##
		past_papers = PastPaper.objects.select_related('subject', 'school').only(
			'subject', 'school', 'title', 'level', 'posted_datetime', 'slug'
		)[:NUM_ITEMS]
		
		context['academic_questions'] = academic_questions
		context['school_questions'] = school_questions
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

		school_questions = SchoolQuestion.objects.annotate(
			total_votes=Count('upvoters', distinct=True)-Count('downvoters', distinct=True)
		).prefetch_related(
			Prefetch('answers', queryset=SchoolAnswer.objects.all().only('id'))
		).filter(total_votes__gt=0)[:NUM_QUESTIONS]
		'''


class NotificationsView(LoginRequiredMixin, TemplateView):
	template_name = "core/notifications.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user = self.request.user

		# get user's notifications from all categories
		general_notifs = user.notifications.filter(category=Notification.GENERAL)
		mentions_notifs = user.notifications.filter(category=Notification.MENTIONS)
		activities_notifs = user.notifications.filter(category=Notification.ACTIVITIES)

		context['general_notifs'] = general_notifs
		context['mentions_notifs'] = mentions_notifs
		context['activities_notifs'] = activities_notifs

		return context
