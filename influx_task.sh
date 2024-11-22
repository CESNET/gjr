#!/bin/bash

python /app/django_server_files/manage.py take_data_from_influx_once
python /app/django_server_files/manage.py store_influx_history_once
