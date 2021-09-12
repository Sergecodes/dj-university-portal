"""
File contains constants that will be used through out application
"""
from datetime import timedelta

EXTERNAL_LINK_SVG = ' \
	<svg x="0px" y="0px" viewBox="0 0 100 100" width="15" height="15" class=""> \
		<path fill="currentColor" d="M18.8,85.1h56l0,0c2.2,0,4-1.8,4-4v-32h-8v28h-48v-48h28v-8h-32l0,0c-2.2,0-4,1.8-4,4v56C14.8,83.3,16.6,85.1,18.8,85.1z" style="--darkreader-inline-fill:currentColor;" data-darkreader-inline-fill=""> \
		</path> \
		<polygon fill="currentColor" points="45.7,48.7 51.3,54.3 77.2,28.5 77.2,37.2 85.2,37.2 85.2,14.9 62.8,14.9 62.8,22.9 71.5,22.9" style="--darkreader-inline-fill:currentColor;" data-darkreader-inline-fill=""> \
		</polygon> \
	</svg>'
EXTERNAL_LINK_ICON = '<i class="fas fa-external-link-alt ms-2" aria-hidden="true"></i>'


# Photo upload key suffixes
ITEM_LISTING_SUFFIX = '_itemlisting_photos'
AD_LISTING_SUFFIX = '_adlisting_photos'
PAST_PAPER_SUFFIX = '_pastpaper_photos'
LOST_ITEM_SUFFIX = '_lostitem_photos'


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
LOST_ITEMS_PHOTOS_UPLOAD_DIR = 'lost_items_photos/'
MAX_LOST_ITEM_PHOTOS = 3
