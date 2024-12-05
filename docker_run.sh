copy files to docker:

scp -i /home/drakis/Documents/cesnet/ssh_keys/galaxy_visualisation /home/drakis/Documents/cesnet/galaxy_visualization/django_server_files/db.sqlite3 debian@10.1.2.21:/data/db.sqlite3 # musí se nejprv dát do ~ a pak až se sudem

scp -i /home/drakis/Documents/cesnet/ssh_keys/galaxy_visualisation /home/drakis/Documents/cesnet/galaxy_visualization/django_server_files/debug.log debian@10.1.2.21:~/debug.log

scp -i /home/drakis/Documents/cesnet/ssh_keys/galaxy_visualisation /home/drakis/Documents/cesnet/galaxy_visualization/django_server_files/.env debian@10.1.2.21:~/.env

scp -i /home/drakis/Documents/cesnet/ssh_keys/galaxy_visualisation /home/drakis/Documents/cesnet/galaxy_visualization/django_server_files/dj_leaflet/settings.py debian@10.1.2.21:~/settings.py

# ještě na serveru
touch ~/cron.log

docker run: 

docker run --name gjr -p 8000:8000 -v /data/db.sqlite3:/app/django_server_files/db.sqlite3 -v /home/debian/debug.log:/app/django_server_files/debug.log -v /home/debian/.env:/app/django_server_files/.env -v /home/debian/settings.py:/app/django_server_files/dj_leaflet/settings.py -v /home/debian/cron.log:/var/log/cron.log -d cerit.io/tomasvondrak/gjr:latest

