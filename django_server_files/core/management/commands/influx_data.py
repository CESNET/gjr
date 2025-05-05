import random
import time
import os
from django.core.management.base import BaseCommand
from core.models import Pulsar, History
from influxdb import InfluxDBClient
from django.utils import timezone
import logging

logger = logging.getLogger('django')
galaxy_iternal_resource_name = "eu_pbs"

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
        # request influxDB
        logger.info("Requesting influxDB with SQL query.")
        results = self.client.query(
            # select all machines (both pulsars and tpvs of galaxy servers)
            'SELECT last("count") FROM "queue_by_destination" GROUP BY "destination_id", "state"'
        )
        logger.info("InfluxDB response successfully stored.")
        db_dict = influxdb_response_to_dict(results.raw)
        # for time optimalization moved into influxdb_response_to_dict function
        # update_pulsar_db(self, db_dict)
        store_history_db(self, db_dict)

# extract raw reponse from influxDB to dictionary and return dict
def influxdb_response_to_dict(response):
    logger.info("Creating data structure with influx data.")

    # init dict for all pulsars data from influxdb of form
    # {"destination_id" :
    #    {"queued": x,
    #     "running": y,
    #     "failed": z}}
    destination_dict = {}

    if 'series' in response:
        destination_info = {
            "queued" : 0,
            "running" : 0,
            "failed" : 0
        }
        for series in response['series']:
            destination_id = series['tags']['destination_id']

            # destination_id preprocessing (nasty thing but at almost each galaxy server there is multiple computing clusters running at the same geolocation so I will call all of them just galaxy pbs - in this case eu_pbs)
            if not "pulsar" in destination_id:
                destination_id = galaxy_iternal_resource_name

            state = series['tags']['state']
            last_count = series['values'][0][1]

            if not destination_id in destination_dict:
                destination_dict[destination_id] = destination_info

            destination_dict[destination_id][state] += last_count
    else:
        logger.error("Bad influxDB response.")

    for pulsar in Pulsar.objects.all():
        if pulsar.name in destination_dict:
            pulsar.queued_jobs = destination_dict[pulsar.name]["queued"]
            pulsar.running_jobs = destination_dict[pulsar.name]["running"]
            pulsar.failed_jobs = destination_dict[pulsar.name]["failed"]
        else:
            pulsar.queued_jobs = 0
            pulsar.running_jobs = 0
            pulsar.failed_jobs = 0
            destination_dict[pulsar.name] = destination_info
        pulsar.save()

    logger.info("Data structure for influx data created.")
    return destination_dict

# updates pulsar database with current influx data
def update_pulsar_db(self, destination_dict):
    logger.info("Updating pulsar db.")
    for pulsar in Pulsar.objects.all():
        if pulsar.name in destination_dict:
            pulsar.queued_jobs = destination_dict[pulsar.name]["queued"]
            pulsar.running_jobs = destination_dict[pulsar.name]["running"]
            pulsar.failed_jobs = destination_dict[pulsar.name]["failed"]
        else:
            pulsar.queued_jobs = 0
            pulsar.running_jobs = 0
            pulsar.failed_jobs = 0
        pulsar.save()
    logger.info("Pulsar db updated.")

# store current influx data into history database
def store_history_db(self, destination_dict):
    logger.info("Updating history db.")
    current_time = timezone.now()
    for destination_id in destination_dict:
        try:
            pulsar = History.objects.get(name=destination_id, timestamp=current_time)
            pulsar.queued_jobs += destination_dict[destination_id]["queued"]
            pulsar.running_jobs += destination_dict[destination_id]["running"]
            pulsar.failed_jobs += destination_dict[destination_id]["failed"]
            pulsar.save()
        except History.DoesNotExist:
            History.objects.create(
                name=destination_id,
                galaxy="usegalaxy.eu",
                queued_jobs=destination_dict[destination_id]["queued"],
                running_jobs=destination_dict[destination_id]["running"],
                failed_jobs=destination_dict[destination_id]["failed"],
                timestamp=current_time
            )
    logger.info("History db updated.")
