#!/bin/sh
python manage.py migrate
gunicorn --bind 0.0.0.0 --timeout 120 chipollino_web.wsgi