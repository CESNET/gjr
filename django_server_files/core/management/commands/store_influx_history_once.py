import random
import time
import os
from django.core.management.base import BaseCommand
from core.models import History
from influxdb import InfluxDBClient
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Store history of InfluxDB"

    # password from environment variable
    influxdb_password = os.environ.get('INFLUXDB_GALAXY_EU_PASSWORD')

    def handle(self, *args, **options):
        client = InfluxDBClient(host="influxdb.galaxyproject.eu", port=8086, username="esg", password=self.influxdb_password, database="galaxy", ssl=True, verify_ssl=True) # TODO make one influx utils where will be function for connecting and queries and that will be used across different scripts, also other utils

        logger.info("Storing influx DB history...")

        results = client.query(
            'SELECT last("count") FROM "queue_by_destination" GROUP BY "destination_id", "state"'
        )

        # Extract raw results
        raw_results = results.raw

        # Store time
        current_time = timezone.now()

        # Check if the series field exists in the raw results
        if 'series' in raw_results:
            for series in raw_results['series']:
                destination_id = series['tags']['destination_id']
                state = series['tags']['state']
                last_count = series['values'][0][1]  # the 'last' value is the second element in the values list

                if "pulsar" in destination_id:
                    add_pulsar_to_history_or_update(self, destination_id, state, last_count, current_time)
                else:
                    add_pulsar_to_history_or_update(self, "eu_pbs", state, last_count, current_time)
        else:
            print("No data found in the query results.")
            logger.warning("No data found in the query results.")

def add_pulsar_to_history_or_update(self, pulsar_name, state, job_num, current_time):
    local_queued_jobs = 0
    local_running_jobs = 0
    local_failed_jobs = 0
    if state == 'queued':
        local_queued_jobs = job_num
    if state == 'running':
        local_running_jobs = job_num
    if state == 'failed':
        local_failed_jobs = job_num
    try:
        pulsar = History.objects.get(name=pulsar_name, timestamp=current_time)
        pulsar.queued_jobs += local_queued_jobs
        pulsar.running_jobs += local_running_jobs
        pulsar.failed_jobs += local_failed_jobs
        pulsar.save()
        print(f"Updated {pulsar.name}: new number of {state} is {job_num}")
        logger.debug(f"Updated {pulsar.name}: new number of {state} is {job_num}")
    except History.DoesNotExist:
        History.objects.create(
            name=pulsar_name,
            galaxy="usegalaxy.eu",
            queued_jobs=local_queued_jobs,
            running_jobs=local_running_jobs,
            failed_jobs=local_failed_jobs,
            timestamp=current_time
        )
