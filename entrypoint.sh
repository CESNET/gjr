#!/bin/bash

# Run database migrations
python /app/django_server_files/manage.py migrate

# Create pulsars
# python /app/django_server_files/manage.py create_pulsars

# Start cron service
cron

# Start the Django development server
exec python /app/django_server_files/manage.py runserver 0.0.0.0:8000
