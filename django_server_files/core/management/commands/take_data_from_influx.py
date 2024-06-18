import random
import time
from django.core.management.base import BaseCommand
from core.models import Pulsar
from influxdb import InfluxDBClient

class Command(BaseCommand):
    help = "Simulate pulsar job computing"

    def handle(self, *args, **options):
        client = InfluxDBClient(host="influxdb.galaxyproject.eu", port=8086, username="esg", password="password", database="galaxy", ssl=True, verify_ssl=True)

        for pulsar in Pulsar.objects.all():
                pulsar.queued_jobs = 0;
                pulsar.running_jobs = 0;
                pulsar.failed_jobs = 0;
                pulsar.save()

        while True:
            print("Pulsar job number updating...")

            # samotné číslo by bylo lepší získat už na úrovni databáze, potom budu ještě potřebovat ty destinations
            results = client.query(
                'SELECT last("count") FROM "queue_by_destination" WHERE ("destination_id" =~ /^pulsar_.*/) GROUP BY "destination_id", "state"'
            )

            # Extract raw results
            raw_results = results.raw

            # Check if the series field exists in the raw results
            if 'series' in raw_results:
                for series in raw_results['series']:
                    destination_id = series['tags']['destination_id']
                    state = series['tags']['state']
                    last_count = series['values'][0][1]  # the 'last' value is the second element in the values list

                    # Output or process each row
                    print(f"Destination ID: {destination_id}, State: {state}, Count: {last_count}")

                    update_pulsar_job_num(self, destination_id, state, last_count)
            else:
                print("No data found in the query results.")

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
        print(f"Updated {pulsar.name}: new job_num is {job_num}")
    except Pulsar.DoesNotExist:
        print(f"Pulsar with name {pulsar_name} does not exist.")
