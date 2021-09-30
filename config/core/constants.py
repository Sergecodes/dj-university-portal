"""
File contains constants that will be used through out application
"""
from datetime import timedelta
from django.utils.translation import gettext_lazy as _


EXTERNAL_LINK_SVG = ' \
	<svg x="0px" y="0px" viewBox="0 0 100 100" width="15" height="15" class=""> \
		<path fill="currentColor" d="M18.8,85.1h56l0,0c2.2,0,4-1.8,4-4v-32h-8v28h-48v-48h28v-8h-32l0,0c-2.2,0-4,1.8-4,4v56C14.8,83.3,16.6,85.1,18.8,85.1z" style="--darkreader-inline-fill:currentColor;" data-darkreader-inline-fill=""> \
		</path> \
		<polygon fill="currentColor" points="45.7,48.7 51.3,54.3 77.2,28.5 77.2,37.2 85.2,37.2 85.2,14.9 62.8,14.9 62.8,22.9 71.5,22.9" style="--darkreader-inline-fill:currentColor;" data-darkreader-inline-fill=""> \
		</polygon> \
	</svg>'
EXTERNAL_LINK_ICON = '<i class="fas fa-external-link-alt ms-2" aria-hidden="true"></i>'


# Photo upload key suffixes (for session)
ITEM_LISTING_SUFFIX = '_itemlisting_photos'
AD_LISTING_SUFFIX = '_adlisting_photos'
PAST_PAPER_SUFFIX = '_pastpaper_photos'
LOST_ITEM_SUFFIX = '_lostitem_photos'
REQUESTED_ITEM_SUFFIX = '_requesteditem_photos'
# Previous points key suffix
# PREVIOUS_POINTS_SUFFIX = 'previous_points'

## USERS APP ##
# set this as minimum points for users.
# when his post is downvoted for instance, if his new points are less than this value,
# set it to this value.
THRESHOLD_POINTS = 5
INITIAL_POINTS = 10
# dummy email
DELETED_USER_EMAIL = 'deleted@gmail.com'


## FLAGGING app ##
# this will be used to identify a bad user(user with some flagged posts)
# a user with this number of points and any flagged post is a bad user.
# also, after deduction from flagging, if user's points is equal to this number, deactivate his account.
# when user's post is disliked, deduct his points and ensure it doesn't reach this number.
# remember that the field `site_points` is a positive integer field
IS_BAD_USER_POINTS = 1
PENALIZE_FLAGGED_USER_POINTS_CHANGE = -10
# reason displayed when flagging an object
FLAG_REASONS = [
	(1, _("Spam | Exists only to promote a service ")),
	(2, _("Abusive | Intended at promoting hatred")),
]
# number of flags before an object is marked as flagged
# after FLAG_ALLOWED flags, an object will be marked flagged.
# and moderators will now be able to delete it.
FLAGS_ALLOWED = 1
# new posts with this count are FLAGGED
IS_FLAGGED_COUNT = FLAGS_ALLOWED + 1


## MARKETPLACE app ##
# minimum number of photos that an item listing must have
MIN_ITEM_PHOTOS_LENGTH = 3
LISTING_PHOTOS_UPLOAD_DIR = 'item_photos/'
AD_PHOTOS_UPLOAD_DIR = 'ad_photos/'


## QA_SITE APP ##
# Changes in points:
	# - like on post(question/answer): +2 points
	# - dislike on post: -4 points
	# - ASK question: +5 points
	# - answer question: +10 points
	# - add or like comment: no change.
# post refers to question or answer

# number of points that user must have to be able to downvote
# remember user is attributed 10 points on signup
REQUIRED_DOWNVOTE_POINTS = 20  
# points deducted(added) to poster after their post is downvoted
POST_DOWNVOTE_POINTS_CHANGE = -4  
# points added to poster after their post is upvoted
POST_UPVOTE_POINTS_CHANGE = +2   
ASK_QUESTION_POINTS_CHANGE = +5
ANSWER_SCHOOL_QUESTION_POINTS_CHANGE = +8
ANSWER_ACADEMIC_QUESTION_POINTS_CHANGE = +10
# each user can have max 2 answers per question
MAX_ANSWERS_PER_USER_PER_QUESTION = 2  
MAX_TAGS_PER_QUESTION = 5

# let user points = 6. after downvoting, we remove say 4 points user is left with 2.
# since 2(his real points) is less than the threshold, it will be set to 5 points.
# thus user didn't have enough points to pay. 
# now if the user recalls the downvote and we had to add points to the user
# it would give 5+4 = 9; which is incorrect !
# in that case, if user_points equals the threshold, we do nothing.
# NOTE that this will be problematic in cases where the user's points = 9;
# coz if user was downvoted, 9-4 = 5. if the downvote is recalled
#  we won't know whether to restore his 9 points.
#  so here, if user has 9 points 
# (THRESHOLD_POINTS=5 + abs(POST_DOWNVOTE_POINTS_CHANGE)), increment it.
RESTRICTED_POINTS = THRESHOLD_POINTS + abs(POST_DOWNVOTE_POINTS_CHANGE)

# Editing
# questions with num_answers > this value can't be edited
QUESTION_CAN_EDIT_NUM_ANSWERS_LIMIT = 1
# questions with vote_count > this value can't be edited
# in other words, only questions with this number of votes and below can be edited
QUESTION_CAN_EDIT_VOTE_LIMIT = 2
# answers with vote_count > this value can't be edited
ANSWER_CAN_EDIT_VOTE_LIMIT = 4
# after this number of minutes, comment can't be edited
COMMENT_CAN_EDIT_TIME_LIMIT = timedelta(minutes=10)
# after this number of votes(upvotes), comment can't be edited
COMMENT_CAN_EDIT_UPVOTE_LIMIT = 4

# Deleting
# questions with num_answers > this value can't be deleted
QUESTION_CAN_DELETE_NUM_ANSWERS_LIMIT = 1
# questions with vote_count > this value can't be deleted
QUESTION_CAN_DELETE_VOTE_LIMIT = 2
# answers with vote_count > this value can't be deleted
ANSWER_CAN_DELETE_VOTE_LIMIT = 2
# after this number of votes(upvotes), comment can't be deleted
COMMENT_CAN_DELETE_UPVOTE_LIMIT = 4


## PAST_PAPERS APP ##
# Changes in points:
	# upload past paper: +5 points (ensure file paper is unique upon posting...)
UPLOAD_PAPER_POINTS_CHANGE = +5
PAST_PAPERS_UPLOAD_DIR = 'past_papers/'
PAST_PAPERS_PHOTOS_UPLOAD_DIR = 'past_paper_photos/'


## SOCIALIZE APP ##
# Changes in points:
	# add social profile: +5 points
CREATE_SOCIAL_PROFILE_POINTS_CHANGE = +5
PROFILE_IMAGE_UPLOAD_DIR = 'profile_pictures/'


### LOST_AND_FOUND APP ###
# Changes in points:
	# post found item: +5 points (you should understand why it doesn't have to be more; user can upload his items...)
PUBLISH_FOUND_ITEM_POINTS_CHANGE = +5
# period for which a post is valid(active)
# determines for how long a post will be displayed on the site.
# LOST_OR_FOUND_ITEM_VALIDITY_PERIOD = timedelta(weeks=1)
LOST_ITEMS_PHOTOS_UPLOAD_DIR = 'lost_items_photos/'
# maximum number of photos to upload for a lost item
MAX_LOST_ITEM_PHOTOS = 3


### REQUESTED ITEMS APP ###
REQUESTED_ITEMS_PHOTOS_UPLOAD_DIR = 'requested_items_photos/'
# maximum number of photos to upload for a requested item
MAX_REQUESTED_ITEM_PHOTOS = 3

