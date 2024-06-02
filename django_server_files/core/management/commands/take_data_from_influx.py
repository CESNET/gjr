import random
import time
from django.core.management.base import BaseCommand
from core.models import Pulsar
from influxdb_client import InfluxDBClient

client = InfluxDBClient(url="https://influxdb.galaxyproject.eu:8086",
                        )

class Command(BaseCommand):
    help = 'Simulate pulsar job computing'

    def handle(self, *args, **options):
        # Define the range of latitude and longitude variation
        lat_lon_var = 0.1  # 0.1 degrees is approximately 11 km
        job_num_var = 10

        while True:
            print("Pulsar job number updating...")

            for pulsar in Pulsar.objects.all():
                # pulsar.latitude = pulsar.latitude + random.uniform(-lat_lon_var, lat_lon_var)
                # pulsar.longitude = pulsar.longitude + random.uniform(-lat_lon_var, lat_lon_var)
                job_num_change = random.randint(-job_num_var, job_num_var)
                pulsar.job_num = pulsar.job_num + job_num_change if pulsar.job_num + job_num_change >= 0 else 0
                pulsar.save()

            time.sleep(2)
