"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!73!8_w-350#rrf(%z@5l5d#i%5v%sjpe%3uf+b9xc3^0zji-@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []
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
	# 'easy_thumbnails',
	'storages',
	'taggit',

	# My apps
	'core',
	'flagging',  # modified django-flag-app
	'lost_and_found',
	'marketplace',
	'notifications',  # modified django-notifications-hq
	'past_papers',
	'qa_site',
	'requested_items',
	'socialize',
	'users',

]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'whitenoise.middleware.WhiteNoiseMiddleware',
	# 'django_hosts.middleware.HostsRequestMiddleware',  # for django_hosts
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.locale.LocaleMiddleware',  # for translation
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	# 'debug_toolbar.middleware.DebugToolbarMiddleware',  # for debug_toolbar
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
			BASE_DIR / 'templates'  # enable finding templates from config/templates directory
		],
		'APP_DIRS': True,   # find templates in 'templates' directory within each app
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.template.context_processors.i18n',  # for i18n.. requests will now include LANGUAGES, LANGUAGE_CODE & LANGUAGE_BIDI
				# 'django.template.context_processors.static',  # added
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',],
		},
	},
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'defaultdb',
		'USER': 'doadmin',
		'PASSWORD': 'w0Ye4iImpnoUyZis',
		'HOST': 'db-postgresql-fra1-45768-do-user-10031233-0.b.db.ondigitalocean.com',
		'PORT': '25060',
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

gettext = lambda s: s
LANGUAGES = (
	('en', gettext('English')),
	('fr', gettext('French')),
)

LOCALE_PATHS = [
	BASE_DIR / 'locale',
]


LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# This logs any emails sent to the console 
# (e.g. so you can copy the password reset link from the console)
USE_ZOHO = True

if USE_ZOHO:
	# see https://www.zoho.com/mail/help/zoho-smtp.html
	EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
	EMAIL_HOST = 'smtppro.zoho.eu'
	EMAIL_HOST_USER = 'users.accounts@camerschools.com'
	EMAIL_HOST_PASSWORD = 'M2Kb4CQdDRdZuQE$'
	EMAIL_PORT = 587
	EMAIL_USE_TLS = True
	EMAIL_USE_SSL = False
	DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

	## ALWAYS USE TLS !! google search
	# SSL refers to Secure Sockets Layer whereas TLS refers to Transport Layer Security.
	## FOR TLS
	# EMAIL_PORT = 587
	# EMAIL_USE_TLS = True
	# EMAIL_USE_SSL = False
	## FOR SSL
	# EMAIL_PORT = 465
	# EMAIL_USE_SSL = True
	# EMAIL_USE_TLS = False
else:
	EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
	DEFAULT_FROM_EMAIL = 'webmaster@localhost'  # default email to use...


AUTHENTICATION_BACKENDS = [
	'django.contrib.auth.backends.ModelBackend',

]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


## USE THIS WHEN NOT WITH AWS...


### django storages (s3) ###
# TODO in production, use environment variables !
# USE_S3 = os.getenv('USE_S3') == 'TRUE'
USE_S3 = True

if USE_S3:
	# according to django-ckeditor, it won't work with S3 
	# through django-storages without this line.
	AWS_QUERYSTRING_AUTH = False
	# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
	# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
	AWS_ACCESS_KEY_ID = 'AKIATDX3R52BAN7MKGF6'
	AWS_SECRET_ACCESS_KEY = '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'
	AWS_STORAGE_BUCKET_NAME = 'camerschools-demobucket'
	# AWS_S3_FILE_OVERWRITE = False
	AWS_S3_CUSTOM_DOMAIN_ = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
	AWS_S3_OBJECT_PARAMETERS = {
		'CacheControl': 'max-age=86400'
	}
	# s3 static settings
	STATIC_LOCATION_ = 'static'
	STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN_}/{STATIC_LOCATION_}/'
	STATICFILES_STORAGE = 'core.storage_backends.StaticStorage'
	STATIC_ROOT = 'static/'

	# s3 public media settings
	PUBLIC_MEDIA_LOCATION_ = 'media'
	MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN_}/{PUBLIC_MEDIA_LOCATION_}/'
	DEFAULT_FILE_STORAGE = 'core.storage_backends.PublicMediaStorage'

	# s3 private media settings
	PRIVATE_MEDIA_LOCATION = 'private'
	PRIVATE_FILE_STORATE = 'core.storage_backends.PrivateMediaStorage'

else:
	# the default file storage backend
	DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'  
	STATIC_URL = '/static/'
	STATIC_ROOT = BASE_DIR / 'core/static'
	STATICFILES_DIRS = [
		BASE_DIR / 'static'
	]

	MEDIA_URL = '/media/'
	MEDIA_ROOT = BASE_DIR / 'media'


### ckEditor ###
# AWS_QUERYSTRING_AUTH = False  # for AWS support
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
	'add_question': {
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
	'add_answer': {
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
	'add_comment': {
		'toolbar': 'Custom',
		'toolbar_Custom': [
			# ['Bold', 'Italic', 'EqnEditor', 'Link', 'CodeSnippet'],
			['Bold', 'Italic', 'Link', 'CodeSnippet'],
		],
		'extraPlugins': 'codesnippet',
		# 'width': '200',
		# 'height': '250'
	},

}


### django-crispy-forms ###
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'
CRISPY_FAIL_SILENTLY = not DEBUG


### django_hosts ###
# ROOT_HOSTCONF = 'config.hosts'
# DEFAULT_HOST = 'www'


### django-taggit ###
TAGGIT_CASE_INSENSITIVE = True
# TAGGIT_TAGS_FROM_STRING = 'core.utils.comma_splitter'
# TAGGIT_STRING_FROM_TAGS = 'core.utils.comma_joiner'


### debug_toolbar ###
if DEBUG == True:
	INTERNAL_IPS = [
		'127.0.0.1',
	]


### modeltranslation ###
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
# MODELTRANSLATION_DEBUG = True
MODELTRANSLATION_FALLBACK_LANGUAGES = ('fr', 'en')



