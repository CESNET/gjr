import random
import time
import os
from django.core.management.base import BaseCommand
from core.models import Pulsar, History, PulsarLongestJobs, PulsarMostUsedTools, PulsarActiveUsers
from influxdb import InfluxDBClient
from django.utils import timezone
import logging
from collections import defaultdict
from datetime import timedelta

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = (
        "Takes data about jobs from galaxy influx database and put them into scheduling database. Data are changed once every 4 hours."
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
        #    "failed"       : num,
        #    "longest"      : [{tool : toolname, hours : num}],
        #    "tools"        : [{tool : toolname, job_num : num}],
        #    "anonymous_jobs"  : num,
        #    "users_jobs"   : [{userid: id, job_num: num}],
        #    "unique_users" : num
        # }
        destination_dict = {}

        self.jobs_info_to_dict(destination_dict)

        # update_schedule_metrics_db(self, destination_dict)

    def jobs_info_to_dict(self, destination_dict):
        logger.info("Storing scheduling jobs data")

        response = self.client.query(
            'SELECT * FROM "galaxy_job_metadata"'
        ).raw

        print(response)

        response = self.client.query(
            'SELECT * FROM "galaxy_job_metrics"'
        ).raw

        print(response)

        response = self.client.query(
            'SELECT * FROM "galaxy_job_state"'
        ).raw

        print(response)

        """
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
        """

        logger.info("Data structure for influx data created.")

# store failed jobs in last hour to history records
def update_schedule_metrics_db(self, destination_dict):
    logger.info("Updating history db.")

    # Retrieve the current time
    current_time = timezone.now()

    # Define the start time as one hour before the current time
    one_hour_ago = current_time - timedelta(hours=1)

    # Iterate over each destination in the dictionary
    for destination_id, stats in destination_dict.items():
        try:
            # Retrieve or create the History object for the given destination_id within the last hour
            pulsars = History.objects.filter(name=destination_id, timestamp__gte=one_hour_ago)

            # If any matching record exists, update its failed jobs count
            if pulsars.exists():
                for pulsar in pulsars:
                    pulsar.failed_jobs = stats.get('failed', 0)
                    pulsar.save()
        except Exception as e:
            logger.error(f"Error updating history for {destination_id}: {str(e)}")

    logger.info("History db updated.")
