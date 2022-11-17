release: python manage.py migrate
web: daphne stockproject.asgi:application --port $PORT --bind 0.0.0.0 -v2
celery: celery -A stockproject.celery worker --pool=solo -l info
celerybeat: celery -A stockproject beat -l INFO
