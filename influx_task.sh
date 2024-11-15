#!/bin/bash

sudo docker exec -it gjr python django_server_files/manage.py take_data_from_influx_once
sudo docker exec -it gjr python django_server_files/manage.py store_influx_history_once
