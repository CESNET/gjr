import time
import os
from django.core.management.base import BaseCommand
from core.models import ScheduleStats
from influxdb import InfluxDBClient
from django.utils import timezone
import logging

logger = logging.getLogger('django')
galaxy_iternal_resource_name = "eu_pbs"

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
        logger.info("Handling update influx data for last four hours (scheduling stats) request.")
        # control influxDB client
        if self.client:
            logger.info("Still successfully connected to InfluxDB.")
        else:
            logger.error("InfluxDB connection failed.")

        galaxy_job_metadata, galaxy_job_state = self.get_job_schedule_data_from_influx()

        # Create dictionaries for easier access
        metadata_columns = galaxy_job_metadata['series'][0]['columns']
        metadata_values = galaxy_job_metadata['series'][0]['values']
        metadata_dict = {row[metadata_columns.index('job_id')]: dict(zip(metadata_columns, row)) for row in metadata_values}

        state_columns = galaxy_job_state['series'][0]['columns']
        state_values = galaxy_job_state['series'][0]['values']
        state_dict = {row[state_columns.index('job_id')]: dict(zip(state_columns, row)) for row in state_values}

        # Join the datasets based on job_id
        combined_data = {}
        for job_id, metadata in metadata_dict.items():
            if job_id in state_dict:
                combined_data[job_id] = {**metadata, **state_dict[job_id]}

        metrics = calculate_metrics(combined_data, 1.5)
        update_schedule_metrics_db(metrics)

    def get_job_schedule_data_from_influx(self):
        logger.info("Storing scheduling jobs data")
        galaxy_job_metadata = self.client.query(
            'SELECT * FROM "galaxy_job_metadata" WHERE time > now() - 14h'
        ).raw
        galaxy_job_state = self.client.query(
            'SELECT * FROM "galaxy_job_state" WHERE time > now() - 14h'
        ).raw
        logger.info("influx data about scheduled jobs saved")
        return galaxy_job_metadata, galaxy_job_state

def update_schedule_metrics_db(metrics):
    logger.info("Updating schedule stats db.")
    current_time = timezone.now()
    dest_dict = {}
    for job_id, job_metrics in metrics.items():
        dest_id = galaxy_iternal_resource_name if not 'pulsar' in job_metrics['dest_id'] else job_metrics['dest_id']
        if not dest_id in dest_dict:
            dest_dict[dest_id] = [{
                'job_id': job_id,
                'response_time': job_metrics['response_time'],
                'mean_slowdown': job_metrics['mean_slowdown'],
                'bounded_slowdown': job_metrics['bounded_slowdown']
            }]
        else:
            dest_dict[dest_id].append({
                'job_id': job_id,
                'response_time': job_metrics['response_time'],
                'mean_slowdown': job_metrics['mean_slowdown'],
                'bounded_slowdown': job_metrics['bounded_slowdown']
            })
    dest_metrics = {}
    for dest_id, jobs in dest_dict.items():
        mean_slowdown_avg = 0
        bounded_slowdown_avg = 0
        response_time_avg = 0
        for job in jobs:
            mean_slowdown_avg += job['mean_slowdown']
            bounded_slowdown_avg += job['bounded_slowdown']
            response_time_avg += job['response_time']
        mean_slowdown_avg /= len(jobs)
        bounded_slowdown_avg /= len(jobs)
        response_time_avg /= len(jobs)
        ScheduleStats.objects.create(
            dest_id=dest_id,
            timestamp=current_time,
            mean_slowndown=mean_slowdown_avg,
            bounded_slowndown=bounded_slowdown_avg,
            response_time=response_time_avg,
        )
    logger.info("Schedule stats db updated.")

def calculate_metrics(data, tau):
    metrics = {}
    for job_id, job_data in data.items():
        job_create_time = job_data['job_create_time']
        final_state_time = job_data['final_state_time']
        dest_id = job_data['destination_id']
        if 'running_start_time' in job_data and final_state_time and job_create_time:
            running_start_time = job_data['running_start_time']
            response_time = final_state_time - job_create_time
            mean_slowdown = response_time / ((final_state_time - running_start_time) if (final_state_time - running_start_time) != 0 else None)
            bounded_slowdown = max(response_time / max((final_state_time - running_start_time), tau), 1)
            metrics[job_id] = {
                'dest_id': dest_id,
                'response_time': response_time,
                'mean_slowdown': mean_slowdown,
                'bounded_slowdown': bounded_slowdown
            }
    return metrics
