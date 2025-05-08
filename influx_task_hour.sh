#!/bin/bash
# Obtain an exclusive lock on the database file with waiting for lock
flock -x /app/db.sqlite3 -c "/usr/local/bin/python /app/django_server_files/manage.py influx_data_hour"
