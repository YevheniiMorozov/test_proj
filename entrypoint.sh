#!/bin/bash

python manage.py migrate --no-input

python manage.py collectstatic --no-input

exec gunicorn server.wsgi:application --bind 0.0.0.0:51117