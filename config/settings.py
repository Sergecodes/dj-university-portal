from decouple import config, Csv
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
SECRET_KEY = config('SECRET_KEY')
USE_CONSOLE_EMAIL = config('USE_CONSOLE_EMAIL', default=True, cast=bool)

# DB
USE_PROD_DB = config('USE_PROD_DB', default=False, cast=bool)
DB_NAME = config('DB_NAME')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_PORT = config('DB_PORT')

# AWS
USE_S3 = config('USE_S3', default=False, cast=bool)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')

# Misc
ENABLE_GOOGLE_TRANSLATE = config('USE_GOOGLE_TRANSLATE', default=False, cast=bool)


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
	# 'django_hosts',
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
	# 'django_hosts.middleware.HostsRequestMiddleware',  # for django_hosts
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.locale.LocaleMiddleware',  # for translation
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'debug_toolbar.middleware.DebugToolbarMiddleware',  # for debug_toolbar
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	# 'django_hosts.middleware.HostsResponseMiddleware',  # for django_hosts
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
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
if USE_PROD_DB:
	pass
else:
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql_psycopg2',
			'NAME': DB_NAME,
			'USER': DB_USER,
			'PASSWORD': DB_PASSWORD,
			'HOST': DB_HOST,
			'PORT': DB_PORT,
		}
	}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

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
if not USE_CONSOLE_EMAIL:
	pass
	# EMAIL_HOST = config('EMAIL_HOST', default='localhost')
	# EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
	# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
	# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
	# EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
	## ALWAYS USE TLS !! google search
	# SSL refers to Secure Sockets Layer whereas TLS refers to Transport Layer Security.
else:
	EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
	DEFAULT_FROM_EMAIL = 'webmaster@localhost'  # default email to use...


AUTHENTICATION_BACKENDS = [
	'django.contrib.auth.backends.ModelBackend',

]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
if USE_S3:
	AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
	AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
	AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
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
			['Bold', 'Italic', 'Table'],
			['NumberedList', 'BulletedList', 'HorizontalRule'],
			['Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight'],
			# '/',  # go to new line
			['Format', 'Font', 'FontSize'],
			['Maximize', 'Preview']
			# ['Maximize', 'Source', 'Preview'] TextColor
		],
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
			['Bold', 'Italic', ],
			# codesnippet plugin needs to be loaded for CodeSnippet to work.
			['Link', 'Blockquote', 'Image', 'CodeSnippet'],
			['NumberedList', 'BulletedList', 'Format', 'HorizontalRule'],
			['Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight'],
			['Undo', 'Redo'],
			['Maximize', 'Preview']
		],
		'tabSpaces': 4,
		'width': 'auto',
		# codesnippet is a built-in plugin
		# eqneditor is for codecogs editor
		# check out installation of codecogs
		# (https://codecogs.com/latex/integration/ckeditor_v4/install.php)
		# 'extraPlugins': 'codesnippet,eqneditor',  
		'extraPlugins': 'codesnippet',
		# 'uiColor': '#ff3333',
	},
	# no CodeSnippet for discussion qstns stuffs
	'add_discuss_question': {
		'toolbar': 'Custom',
		'toolbar_Custom': [
			['Bold', 'Italic', ],
			['Link', 'Blockquote', 'Image', ],
			['NumberedList', 'BulletedList', 'Format', 'HorizontalRule'],
			['Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight'],
			['Undo', 'Redo'],
			['Maximize', 'Preview']
		],
		'tabSpaces': 4,
		'width': 'auto',
		'height': '150px',
	},
	'add_academic_answer': {
		'toolbar': 'Custom',
		'toolbar_Custom': [
			['Bold', 'Italic', ],
			['Link', 'Blockquote', 'Image', 'CodeSnippet'],
			['NumberedList', 'BulletedList', 'Format', 'HorizontalRule'],
			# ['Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight'],
			['Undo', 'Redo'],
			['Maximize', 'Preview']
		],
		'tabSpaces': 4,
		'width': 'auto',
		'extraPlugins': 'codesnippet',
		# 'uiColor': '#ff3333',
	},
	'add_discuss_answer': {
		'toolbar': 'Custom',
		'toolbar_Custom': [
			['Bold', 'Italic', ],
			['Link', 'Blockquote', 'Image', ],
			['NumberedList', 'BulletedList', 'Format', 'HorizontalRule'],
			# ['Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight'],
			['Undo', 'Redo'],
			['Maximize', 'Preview']
		],
		'tabSpaces': 4,
		'width': 'auto',
	},
	'add_academic_comment': {
		'toolbar': 'Custom',
		'toolbar_Custom': [
			# ['Bold', 'Italic', 'EqnEditor', 'Link', 'CodeSnippet'],
			['Bold', 'Italic', 'Link', 'CodeSnippet'],
		],
		'extraPlugins': 'codesnippet',
		'width': 'auto',
	},
	'add_discuss_comment': {
		'toolbar': 'Custom',
		'toolbar_Custom': [
			['Bold', 'Italic', 'Link', ],
		],
		'width': 'auto',
	},

}


### django-crispy-forms ###
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'
CRISPY_FAIL_SILENTLY = not DEBUG


### django_hosts ###
# ROOT_HOSTCONF = 'config.hosts'
# DEFAULT_HOST = 'www'


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
		'thumb': {'size': (2000, 500), 'sharpen': True, },
		'sm_thumb': {'size': (1300, 300), 'sharpen': True, },

		# don't over compress past paper photos...
		# use one thumb alias for past paper to ensure consistency in pdf file
		'pp_thumb': {'size': (2500, 900), 'sharpen': True, },
	}
}
THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE
THUMBNAIL_PRESERVE_EXTENSIONS = True


### modeltranslation ###
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
# MODELTRANSLATION_DEBUG = True
MODELTRANSLATION_FALLBACK_LANGUAGES = ('fr', 'en')


# import django_heroku
# django_heroku.settings(locals())
