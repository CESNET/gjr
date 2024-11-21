FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && apt-get update && apt-get -y install cron

COPY . .

USER root

# COPY cron_script /etc/cron.d/cron_script
# RUN chmod +x /etc/cron.d/cron_script

ADD cron_script /etc/cronjob
RUN crontab /etc/cronjob

# RUN chmod +x ./influx_task.sh

RUN touch /var/log/cron.log

# EXPOSE 8000

# RUN chmod +x ./at_container_start.sh

# CMD ./at_container_start.sh 

CMD ["cron", "-f"]
