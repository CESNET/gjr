# TODO use just take_data_from_influx_once as a library so there is no code duplication

import random
import time
import os
from django.core.management.base import BaseCommand
from core.models import Pulsar
from influxdb import InfluxDBClient
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Pulsar job computing from InfluxDB"

    # password from environment variable
    influxdb_password = os.environ.get('INFLUXDB_GALAXY_EU_PASSWORD')

    def handle(self, *args, **options):
        client = InfluxDBClient(host="influxdb.galaxyproject.eu", port=8086, username="esg", password=self.influxdb_password, database="galaxy", ssl=True, verify_ssl=True)

        while True:
            print("Pulsar job number updating...")
            logger.info("Pulsar job number updating...")

            for pulsar in Pulsar.objects.all():
                pulsar.queued_jobs = 0;
                pulsar.running_jobs = 0;
                pulsar.failed_jobs = 0;
                pulsar.save()

            results = client.query(
                # 'SELECT last("count") FROM "queue_by_destination" WHERE ("destination_id" =~ /^pulsar_.*/) GROUP BY "destination_id", "state"' # just puslars
                'SELECT last("count") FROM "queue_by_destination" GROUP BY "destination_id", "state"' # all machines
            )

            # Extract raw results
            raw_results = results.raw

            # PBS control
            pbs_first_time = True;

            # Check if the series field exists in the raw results
            if 'series' in raw_results:
                for series in raw_results['series']:
                    destination_id = series['tags']['destination_id']
                    state = series['tags']['state']
                    last_count = series['values'][0][1]  # the 'last' value is the second element in the values list

                    # Output or process each row
                    print(f"Destination ID: {destination_id}, State: {state}, Count: {last_count}")
                    logger.info(f"Destination ID: {destination_id}, State: {state}, Count: {last_count}")

                    if "pulsar" in destination_id:
                        update_pulsar_job_num(self, destination_id, state, last_count)
                    else:
                        if pbs_first_time:
                            update_pulsar_job_num(self, "eu_pbs", state, last_count)
                            pbs_first_time = False
                        else:
                            add_to_pulsar_job_num(self, "eu_pbs", state, last_count)
            else:
                print("No data found in the query results.")
                logger.warning("No data found in the query results.")

            time.sleep(10)

def update_pulsar_job_num(self, pulsar_name, state, job_num):
    try:
        pulsar = Pulsar.objects.get(name=pulsar_name)
        if state == 'queued':
            pulsar.queued_jobs = job_num
        if state == 'running':
            pulsar.running_jobs = job_num
        if state == 'failed':
            pulsar.failed_jobs = job_num
        pulsar.save()
        print(f"Updated {pulsar.name}: new number of {state} is {job_num}")
        logger.info(f"Updated {pulsar.name}: new number of {state} is {job_num}")
    except Pulsar.DoesNotExist:
        print(f"Pulsar with name {pulsar_name} does not exist.")
        logger.warning(f"Pulsar with name {pulsar_name} does not exist.")

def add_to_pulsar_job_num(self, pulsar_name, state, job_num):
    try:
        pulsar = Pulsar.objects.get(name=pulsar_name)
        if state == 'queued':
            pulsar.queued_jobs += job_num
        if state == 'running':
            pulsar.running_jobs += job_num
        if state == 'failed':
            pulsar.failed_jobs += job_num
        pulsar.save()
        print(f"Updated pbs {pulsar.name}")
        logger.info(f"Updated pbs {pulsar.name}")
    except Pulsar.DoesNotExist:
        print(f"Pulsar with name {pulsar_name} does not exist.")
        logger.warning(f"Pulsar with name {pulsar_name} does not exist.")
