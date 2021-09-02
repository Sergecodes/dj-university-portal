"""
File contains constants that will be used through out application
"""
from datetime import timedelta

# MARKETPLACE app
MIN_LISTING_PHOTOS_LENGTH = 3
LISTING_PHOTOS_UPLOAD_DIR = 'item_photos/'
AD_PHOTOS_UPLOAD_DIR = 'ad_photos/'


# QA_SITE APP
MAX_TAGS_PER_QUESTION = 5


# PAST_PAPERS APP 
PAST_PAPERS_UPLOAD_DIR = 'past_papers/'
PAST_PAPERS_PHOTOS_UPLOAD_DIR = 'past_paper_photos/'


# SOCIALIZE APP
PROFILE_IMAGE_UPLOAD_DIR = 'profile_pictures/'

### LOST_AND_FOUND APP ###
# period for which a post is valid(active)
# determines for how long a post will be displayed on the site.
LOST_OR_FOUND_ITEM_VALIDITY_PERIOD = timedelta(weeks=1)
