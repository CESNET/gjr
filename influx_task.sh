#!/bin/bash

python /app/galaxy_visualization/django_server_files/manage.py take_data_from_influx_once
python /app/galaxy_visualization/django_server_files/manage.py store_influx_history_once
