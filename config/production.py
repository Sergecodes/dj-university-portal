from .settings import *

# Configure the domain name using the environment variable
# that Azure automatically creates for us.
SITE_HOSTNAME = env('WEBSITE_HOSTNAME')

ADMINS = [x.split(':') for x in env.list('DJANGO_ADMINS', default=[])]
hostname = env('DBHOST')  # DBHOST is only the server name, not the full URL

# DB
DBNAME = env('DBNAME')
DBUSER = env('DBUSER')
DBPASS = env('DBPASS')

ALLOWED_HOSTS = [SITE_HOSTNAME, '.camerschools.site', ]
CSRF_TRUSTED_ORIGINS = [SITE_HOSTNAME, '.camerschools.site', ]

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # this is the default
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
# ALWAYS USE TLS !! google search; SSL = Secure Sockets Layer and TLS = Transport Layer Security.
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', True)
EMAIL_PORT = env.int('EMAIL_PORT', default=587)  # TLS - 587, SSL - 465

# # WhiteNoise configuration
# try:
# 	INSTALLED_APPS.remove('whitenoise.runserver_nostatic')
# except ValueError:
# 	pass

# Static files config
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  

# Configure Postgres database
# DATABASES = {
# 	'default': {
# 		'ENGINE': 'django.db.backends.postgresql',
# 		'NAME': DBNAME,
# 		'HOST': hostname + '.postgres.database.azure.com',
# 		'USER': DBUSER,
# 		'PASSWORD': DBPASS
# 	}
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Remove debug toolbar
try:
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')
except ValueError:
    pass
