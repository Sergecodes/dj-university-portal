web: gunicorn config.wsgi
web: gunicorn config.wsgi:application --preload
release: python3 config/manage.py migrate
