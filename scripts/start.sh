#!/bin/sh
python manage.py migrate
python manage.py collectstatic
gunicorn --bind 0.0.0.0 --timeout 120 chipollino_web.wsgi