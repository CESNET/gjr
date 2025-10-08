import os
from django.core.management.base import BaseCommand
from core.models import Pulsar, Galaxy, History, PulsarLongestJobs, PulsarMostUsedTools, PulsarActiveUsers
from influxdb import InfluxDBClient
from django.utils import timezone
import logging
from collections import defaultdict
from datetime import timedelta

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = (
        "Takes data from galaxy influx database and distributes them into live view (pulsar database) and history view (history database)."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clients = {}  # {galaxy_name: client}
        self.galaxies = Galaxy.objects.all()
        for galaxy in self.galaxies:
            password = os.environ.get(galaxy.influxdb_password_var_name)
            if not password:
                print(f"Env variable {galaxy.influxdb_password_var_name} not set for galaxy {galaxy.name}. Skipping.")
                logger.warning(f"Env variable {galaxy.influxdb_password_var_name} not set for galaxy {galaxy.name}. Skipping.")
                continue
            try:
                client = InfluxDBClient(
                    host=galaxy.influxdb_host,
                    port=galaxy.influxdb_port,
                    username=galaxy.influxdb_username,
                    password=password,
                    database="galaxy",
                    ssl=True,
                    verify_ssl=True
                )
                self.clients[galaxy.name] = client
                logger.info(f"Connected to InfluxDB for galaxy {galaxy.name}.")
            except Exception as e:
                print(f"{e}")
                logger.error(f"Failed to connect to InfluxDB for galaxy {galaxy.name}: {e}")

    def handle(self, *args, **options):
        logger.info("Handling update_influx_data request.")

        current_time = timezone.now()

        for galaxy_name, client in self.clients.items():
            # control influxDB client
            if client:
                logger.info("Still successfully connected to InfluxDB of {galaxy_name}")
            else:
                logger.error("InfluxDB connection failed to {galaxy_name}")

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

            failed_influxdb_response_to_dict(client, destination_dict, galaxy_name)
            longest_influxdb_response_to_dict(client, destination_dict, galaxy_name)
            most_used_tools_influxdb_response_to_dict(client, destination_dict, galaxy_name)
            anonymous_user_influxdb_response_to_dict(client, destination_dict, galaxy_name)
            num_user_running_jobs_influxdb_response_to_dict(client, destination_dict, galaxy_name)
            unique_users_influxdb_response_to_dict(client, destination_dict, galaxy_name)

            update_live_dbs(destination_dict, galaxy_name)
            store_history_db(destination_dict, current_time, galaxy_name)

def failed_influxdb_response_to_dict(client, destination_dict, galaxy_name):
    logger.info("Storing failed jobs data")

    response = client.query(
        'SELECT * FROM "errored_jobs_by_destination" WHERE time > now() - 1h'
    ).raw

    if 'series' in response and len(response['series']) > 0:
        for record in response['series'][0]['values']:
            destination_id = record[2]
            failed_num = int(record[1])

            if not "pulsar" in destination_id:
                destination_id = galaxy_name.split('.')[-1] + '_pbs'

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

def longest_influxdb_response_to_dict(client, destination_dict, galaxy_name):
    logger.info("Storing longest jobs data")

    results = client.query(
        'SELECT * FROM "longest_running_jobs" WHERE time > now() - 1h'
    )

    # Extract the 'values' array from the result's raw data
    result_series = results.raw.get('series', [])
    if result_series and len(result_series) > 0:
        values = result_series[0].get('values', [])
        jobs_by_destination = defaultdict(list)
        for value in values:
            destination_id = value[1] if "pulsar" in value[1] else galaxy_name.split('.')[-1] + '_pbs'
            jobs_by_destination[destination_id].append(value)

        top_jobs_by_destination = {}
        for destination, jobs in jobs_by_destination.items():
            sorted_jobs = sorted(jobs, key=lambda x: x[3], reverse=True)  # Sort by 'hours_since_running'
            top_jobs_by_destination[destination] = sorted_jobs[:5]  # Limit to top 5

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
        logger.error("No data retrieved from InfluxDB.")

def most_used_tools_influxdb_response_to_dict(client, destination_dict, galaxy_name):
    logger.info("Storing most used tools data")

    results = client.query(
        'SELECT * FROM "most_used_tools_by_destination"'
    )

    # Check if there are any series in the response
    result_series = results.raw.get('series', [])
    if not result_series or len(result_series) <= 0:
        logger.error("No data retrieved from InfluxDB.")
        return

    # Extract the 'values' array from the result's raw data
    values = result_series[0].get('values', [])

    temp_destination_data = {}

    for value in values:
        _, destination_id, _, job_count, tool_id = value
        destination_id = destination_id if "pulsar" in destination_id else galaxy_name.split('.')[-1] + '_pbs'
        if destination_id not in temp_destination_data:
            temp_destination_data[destination_id] = []
        temp_destination_data[destination_id].append({
            "tool": tool_id,
            "job_num": job_count
        })

    # Process and store top 3 tools by job_num for each destination
    for destination_id, tools in temp_destination_data.items():
        sorted_tools = sorted(tools, key=lambda x: x["job_num"], reverse=True)
        top_tools = sorted_tools[:3]
        if destination_id not in destination_dict:
            destination_dict[destination_id] = {}
        destination_dict[destination_id]["tools"] = top_tools

    logger.info("Most used tools data successfully stored.")

def anonymous_user_influxdb_response_to_dict(client, destination_dict, galaxy_name):
    logger.info("Storing anonymous user jobs data")

    response = client.query(
        'SELECT * FROM "anonymous_user_jobs_by_destination" WHERE time > now() - 1h'
    )

    if 'series' in response and len(response['series']) > 0:
        for record in response['series'][0]['values']:
            destination_id = record[2]
            failed_num = int(record[1])

            if not "pulsar" in destination_id:
                destination_id = galaxy_name.split('.')[-1] + '_pbs'

            if not destination_id in destination_dict:
                destination_dict[destination_id] = {
                        "anonymous_jobs" : failed_num
                    }
            else:
                if not "anonymous_jobs" in destination_dict[destination_id]:
                    destination_dict[destination_id]["anonymous_jobs"] = failed_num
                destination_dict[destination_id]["anonymous_jobs"] += failed_num
    else:
        logger.error("Bad influxDB response.")

    logger.info("Data structure for influx data created.")

def num_user_running_jobs_influxdb_response_to_dict(client, destination_dict, galaxy_name):
    logger.info("Storing num user jobs data")

    results = client.query(
        'SELECT * FROM "num_user_running_jobs_by_destination" WHERE time > now() - 1h'
    )

    result_series = results.raw.get('series', [])
    if not result_series or len(result_series) <= 0:
        logger.error("No data retrieved from InfluxDB.")
        return

    values = result_series[0].get('values', [])

    temp_user_data = {}

    for value in values:
        time, job_count, destination_id, host, user_id = value
        destination_id = destination_id if "pulsar" in destination_id else galaxy_name.split('.')[-1] + '_pbs'
        if destination_id not in temp_user_data:
            temp_user_data[destination_id] = {}
        if user_id not in temp_user_data[destination_id]:
            temp_user_data[destination_id][user_id] = 0
        temp_user_data[destination_id][user_id] += job_count

    for destination_id, users in temp_user_data.items():
        sorted_users = sorted([{ "userid": k, "job_num": v } for k, v in users.items()],
                            key=lambda x: x["job_num"], reverse=True)
        top_users = sorted_users[:5]
        if destination_id not in destination_dict:
            destination_dict[destination_id] = {}
        destination_dict[destination_id]["users_jobs"] = top_users

    logger.info("Num user jobs data successfully stored.")

def unique_users_influxdb_response_to_dict(client, destination_dict, galaxy_name):
    logger.info("Storing unique user data")

    results = client.query(
        'SELECT * FROM "num_unique_users_jobs_by_destination" WHERE time > now() - 1h'
    )

    result_series = results.raw.get('series', [])
    if not result_series or len(result_series) <= 0:
        logger.error("No data retrieved from InfluxDB.")
        return

    values = result_series[0].get('values', [])
    for value in values:
        timestamp, destination_id, host, state, unique_user_count = value
        destination_id = destination_id if "pulsar" in destination_id else galaxy_name.split('.')[-1] + '_pbs'
        if destination_id not in destination_dict:
            destination_dict[destination_id] = {}
        destination_dict[destination_id]["unique_users"] = unique_user_count

    logger.info("Unique user data successfully stored.")

# updates pulsar database with current influx data
def update_live_dbs(destination_dict, galaxy_name):
    logger.info(f"Updating live dbs of {galaxy_name}.")
    # Pulsar table
    for pulsar in Pulsar.objects.all():
        if pulsar.name in destination_dict:
            pulsar.failed_jobs = destination_dict[pulsar.name]["failed"] if "failed" in destination_dict[pulsar.name] else 0
            pulsar.anonymous_jobs = destination_dict[pulsar.name]["anonymous_jobs"] if "anonymous_jobs" in destination_dict[pulsar.name] else 0
            pulsar.unique_users = destination_dict[pulsar.name]["unique_users"] if "unique_users" in destination_dict[pulsar.name] else 0
        pulsar.save()
    # PulsarLongestJobs table
    PulsarLongestJobs.objects.all().delete()
    for destination_id, info_list in destination_dict.items():
        try:
            pulsar_instance = Pulsar.objects.get(name=destination_id)
        except Pulsar.DoesNotExist:
            continue
        if "longest" in info_list:
            for record in info_list["longest"]:
                PulsarLongestJobs.objects.create(
                        pulsar=pulsar_instance,
                        tool=record["tool"],
                        hours=record["hours"]
                    )
    # PulsarMostUsedTools table
    PulsarMostUsedTools.objects.all().delete()
    for destination_id, info_list in destination_dict.items():
        try:
            pulsar_instance = Pulsar.objects.get(name=destination_id)
        except:
            continue
        if "tools" in info_list:
            for record in info_list["tools"]:
                PulsarMostUsedTools.objects.create(
                        pulsar=pulsar_instance,
                        tool=record["tool"],
                        job_num=record["job_num"]
                    )
    # PulsarActiveUsers table
    PulsarActiveUsers.objects.all().delete()
    for destination_id, info_list in destination_dict.items():
        try:
            pulsar_instance = Pulsar.objects.get(name=destination_id)
        except:
            continue
        if "users_jobs" in info_list:
            for record in info_list["users_jobs"]:
                PulsarActiveUsers.objects.create(
                        pulsar=Pulsar.objects.get(name=destination_id),
                        user_id=record["userid"],
                        job_num=record["job_num"]
                    )
    logger.info(f"Live dbs updated of {galaxy_name}.")

# store failed jobs in last hour to history records
def store_history_db(destination_dict, current_time, galaxy_name):
    logger.info(f"Updating history db of {galaxy_name}.")
    one_hour_ago = current_time - timedelta(hours=1)
    for destination_id, stats in destination_dict.items():
        try:
            pulsars = History.objects.filter(name=destination_id, galaxy=galaxy_name, timestamp__gte=one_hour_ago)
            if pulsars.exists():
                for pulsar in pulsars:
                    pulsar.failed_jobs = stats.get('failed', 0)
                    pulsar.save()
        except Exception as e:
            logger.error(f"Error updating history for {destination_id}: {str(e)} of {galaxy_name}")
    logger.info(f"History db updated of {galaxy_name}.")
