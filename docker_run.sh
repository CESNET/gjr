docker run --name gjr -p 8000:8000 -v /data/gjr_data/db.sqlite3:/app/django_server_files/db.sqlite3 -v /home/debian/debug.log:/app/django_server_files/debug.log -v /home/debian/.env:/app/django_server_files/.env -v /home/debian/settings.py:/app/django_server_files/dj_leaflet/settings.py -v /home/debian/cron.log:/var/log/cron.log -d cerit.io/tomasvondrak/gjr:mounting

