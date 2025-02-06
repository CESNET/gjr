#!/bin/bash
export DJANGO_SETTINGS_MODULE=/app/django_server_files/dj_leaflet/settings.py
/usr/local/bin/python /app/django_server_files/manage.py update_influx_data
