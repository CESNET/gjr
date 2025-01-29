from django.core.management.base import BaseCommand
import rrdtool
import influxdb

class Command(BaseCommand):
    help = 'Update RRD database with data from InfluxDB'

    # password from environment variable
    influxdb_password = os.environ.get('INFLUXDB_GALAXY_EU_PASSWORD')

    def handle(self, *args, **kwargs):
        client = InfluxDBClient(host="influxdb.galaxyproject.eu", port=8086, username="esg", password=self.influxdb_password, database="galaxy", ssl=True, verify_ssl=True)

        results = client.query(
            'SELECT last("count") FROM "queue_by_destination" GROUP BY "destination_id", "state"'
        )

        # Extract raw results
        raw_results = results.raw

        # Store time
        current_time = timezone.now()

        # Check if the series field exists in the raw results
        if 'series' in raw_results:

            pulsar_dict = {} # key: pulsar name, value: dict = {failed_jobs: num, queued_jobs: num, running_jobs: num}

            for series in raw_results['series']:
                destination_id = series['tags']['destination_id']
                state = series['tags']['state']
                last_count = series['values'][0][1]  # the 'last' value is the second element in the values list

                if "pulsar" in destination_id:
                    # update pulsar dict
                    add_pulsar_to_history_or_update(self, destination_id, state, last_count, current_time)
                else:
                    # update pulsar dict
                    add_pulsar_to_history_or_update(self, "eu_pbs", state, last_count, current_time)

            # after all update rrd at once with whole dict
        else:
            print("No data found in the query results.")
            logger.warning("No data found in the query results.")

def update_pulsar_rrd(self, pulsar_name, state, job_num):
    local_queued_jobs = 0
    local_running_jobs = 0
    local_failed_jobs = 0
    if state == 'queued':
        local_queued_jobs = job_num
    if state == 'running':
        local_running_jobs = job_num
    if state == 'failed':
        local_failed_jobs = job_num

    rrd_path = f'rrd/{pulsar_name}.rrd'
    rrdtool.update(rrd_path, f'N:{local_running_jobs}:{local_waiting_jobs}:{local_failed_jobs}')                self.stdout.write(self.style.SUCCESS(f'Successfully updated RRD for {pulsar_name}'))
