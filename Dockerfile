FROM python:3.12
WORKDIR /app

# Add cron scrpt file in the cron directory
ADD crontab /etc/cron.d/run_influx_rutines

# copy files to working dir
COPY . .

# download dependecies
RUN apt-get update && apt-get install gcc make
RUN apt-get install -y librrd-dev
RUN pip install --no-cache-dir -r requirements.txt && apt-get update

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/run_influx_rutines
RUN chmod +x /app/influx_task.sh

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

#Install Cron
RUN apt-get update
RUN apt-get -y install cron

# open port
EXPOSE 8000

# Run the command on container startup
CMD cron && python django_server_files/manage.py migrate && python django_server_files/manage.py create_pulsars && python django_server_files/manage.py runserver 0.0.0.0:8000
