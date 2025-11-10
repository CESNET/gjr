#!/bin/bash

# Run database migrations
python /app/django_server_files/manage.py migrate
python /app/django_server_files/manage.py influx_data
python /app/django_server_files/manage.py influx_data_hour
python /app/django_server_files/manage.py influx_data_4hours

# Create pulsars
# python /app/django_server_files/manage.py create_pulsars

# Start cron service
cron

# Start the Django development server
# exec python /app/django_server_files/manage.py runserver 0.0.0.0:8000

# Start Gunicorn server
exec gunicorn dj_leaflet.wsgi:application --bind 0.0.0.0:8000
