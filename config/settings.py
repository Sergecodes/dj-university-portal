import environ
import os
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from pathlib import Path

from core.constants import MAX_TEXT_LENGTH

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/
# django-environ
env = environ.Env()
env_file = os.path.join(BASE_DIR, '.env')
env.read_env(env_file)

DEBUG = env.bool('DEBUG', True)
SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# DB
DEV_DB_NAME = env('DEV_DB_NAME', default=None)
DEV_DB_USER = env('DEV_DB_USER', default=None)
DEV_DB_PASSWORD = env('DEV_DB_PASSWORD', default=None)
DEV_DB_HOST = env('DEV_DB_HOST', default=None)
DEV_DB_PORT = env.int('DEV_DB_PORT', default=None)

# Redis
REDIS_URL = env('REDIS_URL', default=None)

## Misc
# Validate or not whether at least one of a user's numbers must support whatsapp
CHECK_WHATSAPP = env.bool('CHECK_WHATSAPP', default=False)
USE_S3 = env.bool('USE_S3', default=False)
ENABLE_GOOGLE_TRANSLATE = env.bool('USE_GOOGLE_TRANSLATE', False)

AUTH_USER_MODEL = 'users.User'
SITE_NAME = 'CamerSchools'

# Application definition

INSTALLED_APPS = [
	'modeltranslation',  # this has to come before admin app to enable admin integration
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
   # 'whitenoise.runserver_nostatic',  # Added, needed in development only
	'django.contrib.staticfiles',
	# 'django.contrib.sites',   # added
	'django.contrib.humanize', # added

	### 3rd party ###
	# 'captcha',
	'ckeditor',
	'ckeditor_uploader',
	'crispy_forms',
	'crispy_bootstrap5',
	'django_extensions',
	'django_filters',
	# 'debug_toolbar',
	'easy_thumbnails',
	'storages',
	'taggit',
   'taggit_selectize',

	# My apps
	'core',
	'flagging',  # modified django-flag-app
	'lost_or_found',
	'marketplace',
	'notifications',  # modified django-notifications-hq
	'past_papers',
	'qa_site',
	'requested_items',
	'socialize',
	'users',

]

if DEBUG:
	INSTALLED_APPS.append('debug_toolbar')

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
   # 'whitenoise.middleware.WhiteNoiseMiddleware',  # for whitenoise
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.locale.LocaleMiddleware',  # for translation
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'debug_toolbar.middleware.DebugToolbarMiddleware',  # for debug_toolbar
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [
			# by default, django template loader will look within each app for a 'templates' folder...
			# i.e. app_name/templates/app_name/..  (place templates here) to avoid namespace issues
			BASE_DIR / 'templates',  # enable finding templates from config/templates directory
		],
		'APP_DIRS': True,   # find templates in 'templates' directory within each app
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				# for i18n.. requests will now include LANGUAGES, LANGUAGE_CODE & LANGUAGE_BIDI
				'django.template.context_processors.i18n',  
				# 'django.template.context_processors.static',  # added
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',],
		},
	},
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': DEV_DB_NAME,
		'USER': DEV_DB_USER,
		'PASSWORD': DEV_DB_PASSWORD,
		'HOST': DEV_DB_HOST,
		'PORT': DEV_DB_PORT,
	}
}


# Caching (https://github.com/jazzband/django-redis, https://docs.djangoproject.com/en/3.2/topics/cache/)
if REDIS_URL:
	SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

	CACHES = {
		'default': {
			'BACKEND': 'django_redis.cache.RedisCache',
			'LOCATION': REDIS_URL,
			'OPTIONS': {
				'CLIENT_CLASS': 'django_redis.client.DefaultClient',
			}
		}
	}

	# CACHES = {
	# 	'default': {
	# 		'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
	# 		'LOCATION': 'cache_table',
	# 	}
	# }
	# python manage.py createcachetable --dry-run

	# CACHES = {
	# 	'default': {
	# 		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
	# 		'TIMEOUT': 300,  # The default(300s = 5mins)
	# 		# 'TIMEOUT': 60 * 60 * 24,  # 86400(s)=24h
	# 	}
	# }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
	('en', _('English')),
	('fr', _('French')),
)

LOCALE_PATHS = [
	BASE_DIR / 'locale',
]

LOGIN_URL = reverse_lazy('users:login')
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# This logs any emails sent to the console 
# (e.g. so you can copy the password reset link from the console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'webmaster@localhost'  # default email to use...


AUTHENTICATION_BACKENDS = [
	'django.contrib.auth.backends.ModelBackend',

]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
if USE_S3:
	AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
	AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
	AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
	AWS_S3_OBJECT_PARAMETERS = {
		# use a high value so that files are cached for long (6months=2628000)
		# however, updates on files won't work ... and file name  should be changed after updates..
		# for now, set it to 1 day(86400secs)
		# 1month = 2.628e+6 (2628000secs)
		'CacheControl': 'max-age=86400'
	}
	AWS_S3_SIGNATURE_VERSION = 's3v4'
	# AWS_S3_FILE_OVERWRITE = False
	AWS_DEFAULT_ACL = None
	AWS_S3_VERIFY = True

	# according to django-ckeditor, it won't work with S3 
	# through django-storages without this line.
	AWS_QUERYSTRING_AUTH = False

	## Note: Variables ending in '_' are user-defined, not required or used by a package
	AWS_S3_CUSTOM_DOMAIN_ = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
	AWS_S3_OBJECT_PARAMETERS = {
		# use a high value so that files are cached for long (6months=2628000)
		# however, updates on files won't work ... and file name  should be changed after updates..
		# for now, set it to 1 day(86400secs)
		# 1month = 2.628e+6 (2628000secs)
		'CacheControl': 'max-age=86400'
	}
	# s3 static settings
	# STATIC_LOCATION_ = 'static'
	STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN_}/static/'
	STATICFILES_STORAGE = 'core.storage_backends.StaticStorage'
	STATIC_ROOT = 'staticfiles/'
	# We don't need STATIC_URL here since to upload files, we'll run collectstatic
	# and all static files will be placed in the STATIC_ROOT folder

	# s3 public media settings. 
	# This var is also used in core.storages to set the location of media files
	PUBLIC_MEDIA_LOCATION_ = 'media'
	MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN_}/{PUBLIC_MEDIA_LOCATION_}/'
	MEDIA_ROOT = MEDIA_URL
	DEFAULT_FILE_STORAGE = 'core.storage_backends.PublicMediaStorage'

	# # s3 private media settings
	# PRIVATE_MEDIA_LOCATION = 'private'
	# PRIVATE_FILE_STORAGE = 'core.storage_backends.PrivateMediaStorage'
else:
	DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'  
	STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
	STATIC_URL = 'static/'
	STATIC_ROOT = BASE_DIR / 'staticfiles'
	# STATICFILES_DIRS = [
	# 	BASE_DIR / 'static'
	# ]

	MEDIA_URL = 'media/'
	MEDIA_ROOT = BASE_DIR / 'media'


### ckEditor ###
CKEDITOR_UPLOAD_PATH = 'ckuploads/'   # create a directory in media directory
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_ALLOW_NONIMAGE_FILES = False

CKEDITOR_CONFIGS = {
	'default': {
		'toolbar': 'none',
	},
	'listing_description': {
		'toolbar': 'Custom',
		'toolbar_Custom': [
			['Bold', 'Italic', 'Underline', 'Strike'],
			['Subscript', 'Superscript'],
			['Table', 'NumberedList', 'BulletedList', 'HorizontalRule'],
			['Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', '-', 'BidiLtr', 'BidiRtl'],
			'/',  # go to new line
			['Format', 'Font', 'FontSize'],
			['Undo', 'Redo', '-', 'Maximize', 'Preview']
		],
		'extraPlugins': 'wordcount',
		# https://ckeditor.com/cke4/addon/wordcount
		'wordcount': {
			'showRemaining': True,
			'showParagraphs': False,
			'showCharCount': True,
			'showWordCount': False,
			'maxCharCount': MAX_TEXT_LENGTH,
		},
		'tabSpaces': 4,
		# this will be set to the ck-editor instance instead
		# (id='cke_id_description' and class='cke_1 cke ... ')
		'width': 'auto' 
		# 'uiColor': '#ff3333',
	},
	'add_academic_question': {
		'toolbar': 'Custom',
		'toolbar_Custom': [
			# 'EqnEditor' is from CodeCogs, it needs the eqneditor plugin
			['Bold', 'Italic', 'Underline', 'Strike'],
			['Subscript', 'Superscript'],
			# codesnippet plugin needs to be loaded for CodeSnippet to work.
			['Link', 'Blockquote', 'Image', '-', 'Table', 'EqnEditor', 'CodeSnippet'],
			['NumberedList', 'BulletedList'],
			'/',
			['Format', 'HorizontalRule'],
			['Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', '-', 'BidiLtr', 'BidiRtl'],
			['Undo', 'Redo', '-', 'Maximize', 'Preview']
		],
		# codesnippet is a built-in plugin
		# eqneditor is for codecogs editor
		# check out installation of codecogs
		# (https://codecogs.com/latex/integration/ckeditor_v4/install.php)
		'extraPlugins': 'codesnippet,eqneditor,wordcount',
		'wordcount': {
			'showRemaining': True,
			'showParagraphs': False,
			'showCharCount': True,
			'showWordCount': False,
			'maxCharCount': MAX_TEXT_LENGTH,
		},
		'tabSpaces': 4,
		'width': 'auto',
		# 'uiColor': '#ff3333',
	},
	# no CodeSnippet for discussion qstns stuffs
	'add_discuss_question': {
		'toolbar': 'Custom',
		'toolbar_Custom': [
			['Bold', 'Italic', 'Underline'],
			['Link', 'Blockquote', 'Image', ],
			['NumberedList', 'BulletedList', 'Format', 'HorizontalRule'],
			['Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', '-', 'BidiLtr', 'BidiRtl'],
			['Undo', 'Redo', '-', 'Maximize', 'Preview']
		],
		'extraPlugins': 'wordcount',
		'wordcount': {
			'showRemaining': True,
			'showParagraphs': False,
			'showCharCount': True,
			'showWordCount': False,
			'maxCharCount': MAX_TEXT_LENGTH,
		},
		'tabSpaces': 4,
		'width': 'auto',
		'height': '150px',
	},

	# Not really used
	'add_academic_comment': {
		'toolbar': 'Custom',
		# Commented because they aren't actually used 
		'toolbar_Custom': [
			# ['Bold', 'Italic', ],
			# ['Link', 'Blockquote', 'Image', 'CodeSnippet'],
			# ['NumberedList', 'BulletedList', 'Format', 'HorizontalRule'],
			# # ['Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight'],
			# ['Undo', 'Redo'],
			# ['Maximize', 'Preview']
		],
		'tabSpaces': 4,
		'width': 'auto',
		'extraPlugins': 'codesnippet',
		# 'uiColor': '#ff3333',
	},
	'add_discuss_comment': {
		'toolbar': 'Custom',
		'toolbar_Custom': [
			# ['Bold', 'Italic', 'Link', ],
		],
		'width': 'auto',
	},
}


### django-crispy-forms ###
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'
CRISPY_FAIL_SILENTLY = not DEBUG


### django-taggit & taggit_selectize ###
TAGGIT_CASE_INSENSITIVE = True
# Demanded by taggit_selectize to match functionality of selectize
TAGGIT_SELECTIZE_THROUGH = 'qa_site.models.QuestionTag'
TAGGIT_TAGS_FROM_STRING = 'taggit_selectize.utils.parse_tags'
TAGGIT_STRING_FROM_TAGS = 'taggit_selectize.utils.join_tags'
TAGGIT_SELECTIZE = {
   'JS_FILENAMES': (
		"taggit_selectize/js/selectize.js", 
		"js/taggit-selectize.extra.js"
	),
	'PRELOAD': False,
	'SELECT_ON_TAB': False,
	'REMOVE_BUTTON': True,
	'RESTORE_ON_BACKSPACE': True,
	'DELIMITER': ' ',
}


### easy_thumbnails ###
THUMBNAIL_ALIASES = {
	# width and height are required for size
	'': {
		# sharpen makes the image brighter(sharper)
		'thumb': {'size': (1800, 500), 'sharpen': True, },
		'sm_thumb': {'size': (1100, 300), 'sharpen': True, },

		# don't over compress past paper photos...
		# use one thumb alias for past paper to ensure consistency in pdf file
		'pp_thumb': {'size': (2300, 700), 'sharpen': True, },
	}
}
THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE
THUMBNAIL_NAMER = 'easy_thumbnails.namers.hashed'
THUMBNAIL_PRESERVE_EXTENSIONS = True


### modeltranslation ###
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
# MODELTRANSLATION_DEBUG = True
MODELTRANSLATION_FALLBACK_LANGUAGES = ('fr', 'en')

