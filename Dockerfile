FROM python:3.12
WORKDIR /app

# Add cron scrpt file in the cron directory
ADD crontab /etc/cron.d/run_influx_rutines

# copy files to working dir
COPY . .

# download dependecies
RUN apt-get update && apt-get install -y gcc make sqlite3
RUN apt-get install -y librrd-dev
RUN pip --default-timeout=200 install --no-cache-dir -r requirements.txt && apt-get update

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/run_influx_rutines
RUN chmod +x /app/influx_task.sh
RUN chmod +x /app/influx_task_hour.sh
RUN chmod +x /app/sqlite_backup.sh

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

#Install Cron
RUN apt-get update
RUN apt-get -y install cron

# open port
EXPOSE 8000

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script to start all services
ENTRYPOINT ["/app/entrypoint.sh"]
