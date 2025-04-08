import random
import time
import os
from django.core.management.base import BaseCommand
from core.models import Pulsar, History
from influxdb import InfluxDBClient
from django.utils import timezone
import logging
from collections import defaultdict

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = (
        "Takes data from galaxy influx database and distributes them into live view (pulsar database) and history view (history database)."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # password from environment variable
        self.influxdb_password = os.environ.get('INFLUXDB_GALAXY_EU_PASSWORD')

        # Ensure password is retrieved
        if not self.influxdb_password:
            logger.warning("INFLUXDB_GALAXY_EU_PASSWORD environment variable is not set.")

        # Establish the InfluxDB client
        try:
            logger.info("Connecting to influxDB.")
            self.client = InfluxDBClient(
                host="influxdb.galaxyproject.eu",
                port=8086,
                username="esg",
                password=self.influxdb_password,
                database="galaxy",
                ssl=True,
                verify_ssl=True
            )
            logger.info("Finished connecting to influxDB.")

        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            self.client = None

    def handle(self, *args, **options):
        logger.info("Handling update_influx_data request.")

        # control influxDB client
        if self.client:
            logger.info("Still successfully connected to InfluxDB.")
        else:
            logger.error("InfluxDB connection failed.")

        # init dict for all pulsars data from influxdb of form
        # {"destination_id" : {
        #    "failed"  : num,
        #    "longest" : [{tool : toolname, hours : num}],
        #    "tools"   : []
        # }
        destination_dict = {}

        # self.failed_influxdb_response_to_dict(destination_dict)
        # self.longest_influxdb_response_to_dict(destination_dict)
        self.anonymous_user_influxdb_response_to_dict(destination_dict)

        print(destination_dict)

        # update_pulsar_db(self, destination_dict)
        # store_history_db(self, destination_dict)

    def failed_influxdb_response_to_dict(self, destination_dict):
        logger.info("Storing failed jobs data")

        response = self.client.query(
            'SELECT * FROM "errored_jobs_by_destination" WHERE time > now() - 1h'
        ).raw

        if 'series' in response:
            for record in response['series'][0]['values']:
                destination_id = record[2]
                failed_num = int(record[1])

                if not "pulsar" in destination_id:
                    destination_id = "eu_pbs"

                # check if destination is already in dict
                if not destination_id in destination_dict:
                    destination_dict[destination_id] = {
                            "failed" : failed_num
                        }
                else:
                    if not "failed" in destination_dict[destination_id]:
                        destination_dict[destination_id]["failed"] = failed_num
                    destination_dict[destination_id]["failed"] += failed_num

        else:
            logger.error("Bad influxDB response.")

        logger.info("Data structure for influx data created.")
        return destination_dict

    def longest_influxdb_response_to_dict(self, destination_dict):
        logger.info("Storing failed jobs data")

        results = self.client.query(
            'SELECT * FROM "longest_running_jobs" WHERE time > now() - 1h'
        )

        # Extract the 'values' array from the result's raw data
        result_series = results.raw.get('series', [])
        if result_series:
            values = result_series[0].get('values', [])

            # Group jobs by destination_id
            jobs_by_destination = defaultdict(list)
            for value in values:
                destination_id = value[1] if "pulsar" in value[1] else "eu_pbs"  # Assuming this is the index for 'destination_id'
                jobs_by_destination[destination_id].append(value)

            # Sort each group by 'hours_since_running' and limit to top 5
            top_jobs_by_destination = {}
            for destination, jobs in jobs_by_destination.items():
                sorted_jobs = sorted(jobs, key=lambda x: x[3], reverse=True)  # Sort by 'hours_since_running'
                top_jobs_by_destination[destination] = sorted_jobs[:5]  # Limit to top 5

            # Output the results
            for destination, top_jobs in top_jobs_by_destination.items():
                if not destination in destination_dict:
                    destination_dict[destination] = {}
                destination_dict[destination]["longest"] = []
                for job in top_jobs:
                    destination_dict[destination]["longest"].append({
                        "tool" : job[5],
                        "hours" : job[3]
                    })
        else:
            print("No data retrieved from InfluxDB.")

    def anonymous_user_influxdb_response_to_dict(self, destination_dict):
        logger.info("Storing anonymous user jobs data")

        results = self.client.query(
            'SELECT * FROM "anonymous_user_jobs_by_destination"'
        )

        print(results.raw)


# updates pulsar database with current influx data
def update_pulsar_db(self, destination_dict):
    logger.info("Updating pulsar db.")

    for pulsar in Pulsar.objects.all():
        if pulsar.name in destination_dict:
            pulsar.failed_jobs = destination_dict[pulsar.name]["failed"] if "failed" in destination_dict[pulsar.name] else 0
        else:
            pulsar.running_jobs = 0
            pulsar.queued_jobs = 0
            pulsar.failed_jobs = 0
        # saving changed pulsar (TODO question is if I should not save all pulsars at once with some more specified command)
        pulsar.save()

    logger.info("Pulsar db updated.")

# store current influx data into history database
# TODO failed jobs store to every record in last hour?
def store_history_db(self, destination_dict):
    logger.info("Updating history db.")

    # Store time
    current_time = timezone.now()

    for destination_id in destination_dict:
        try:
            pulsar = History.objects.get(name=destination_id, timestamp=current_time)
            pulsar.failed_jobs += destination_dict[destination_id]["failed"]
            pulsar.save()
        except History.DoesNotExist:
            History.objects.create(
                name=destination_id,
                galaxy="usegalaxy.eu",
                running_jobs=0,
                queued_jobs=0,
                failed_jobs=destination_dict[destination_id]["failed"] if "failed" in destination_dict[destination_id] else 0,
                timestamp=current_time
            )

    logger.info("History db updated.")
