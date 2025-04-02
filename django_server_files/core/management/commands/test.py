import random
import time
import os
from django.core.management.base import BaseCommand
from core.models import Pulsar, History
from influxdb import InfluxDBClient
from django.utils import timezone
import logging

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

        # request influxDB

        logger.info("Requesting influxDB with SQL query.")

        results = self.client.query(
            # select all machines (both pulsars and tpvs of galaxy servers)
            # 'SELECT last("count") FROM "longest_running_jobs"'
            'SELECT * FROM "longest_running_jobs"'
        )

        print(results.raw)
