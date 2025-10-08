import os
from django.core.management.base import BaseCommand
from core.models import Galaxy, Pulsar, History
from influxdb import InfluxDBClient
from django.utils import timezone
import logging

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = (
        "Takes data from connected galaxy servers influx databases (which are in db) and distributes them into live view (pulsar database) and history view (history database)."
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
        # init dict for all galaxy data from influxdbs of form
        # {"galaxy_name" : 
        #   {"destination_id" :
        #       {
        #           "queued" : x,
        #           "running" : y
        #       }
        #   }
        # }
        db_dict = {}
        for galaxy_name, client in self.clients.items():
            if client:
                logger.info("Still successfully connected to InfluxDB of " + galaxy_name)
            else:
                logger.error("InfluxDB connection failed of " + galaxy_name)
            logger.info("Requesting influxDB with SQL query of " + galaxy_name)
            results = client.query(
                # select all machines (both pulsars and tpvs of galaxy servers)
                'SELECT last("count") FROM "queue_by_destination" GROUP BY "destination_id", "state"'
            )
            logger.info("InfluxDB response successfully stored from " + galaxy_name)
            db_dict[galaxy_name] = influxdb_response_to_dict(results.raw, galaxy_name)
        print(db_dict)
        update_pulsar_db(self, db_dict)
        store_history_db(self, db_dict)

# extract raw reponse from influxDB to dictionary and return dict
def influxdb_response_to_dict(response, galaxy_name):
    logger.info("Creating data structure with influx data.")

    # init dict for all pulsars data from influxdb of one galaxy of form
    # {"destination_id" :
    #    {
    #     "queued" : x,
    #     "running" : y
    #    }
    # }
    destination_dict = {}

    if 'series' in response:
        for series in response['series']:
            destination_id = series['tags']['destination_id']

            # destination_id preprocessing (nasty thing but at almost each galaxy server there is multiple computing clusters running at the same geolocation so I will call all of them just galaxy pbs - in this case eu_pbs)
            if not "pulsar" in destination_id:
                destination_id = galaxy_name.split('.')[-1] + '_pbs'

            state = series['tags']['state']
            last_count = series['values'][0][1]

            if not destination_id in destination_dict:
                destination_dict[destination_id] = {
                    "queued": 0,
                    "running": 0
                }

            destination_dict[destination_id][state] += last_count
    else:
        logger.error("Bad influxDB response.")

    logger.info("Data structure for influx data created.")
    return destination_dict

# updates pulsar database with current influx data
def update_pulsar_db(self, db_dict):
    logger.info("Updating pulsar db.")
    for galaxy_name in db_dict:
        for pulsar in Pulsar.objects.filter(galaxy=galaxy_name):
            if pulsar.name in db_dict[galaxy_name]:
                pulsar.queued_jobs = db_dict[galaxy_name][pulsar.name]["queued"]
                pulsar.running_jobs = db_dict[galaxy_name][pulsar.name]["running"]
            else:
                pulsar.queued_jobs = 0
                pulsar.running_jobs = 0
                db_dict[galaxy_name][pulsar.name] = {
                    "queued": 0,
                    "running": 0
                }
            pulsar.save()
    logger.info("Pulsar db updated.")

# store current influx data into history database
def store_history_db(self, db_dict):
    logger.info("Updating history db.")
    current_time = timezone.now()
    for galaxy_name in db_dict:
        for destination_id in db_dict[galaxy_name]:
            try:
                pulsar = History.objects.get(name=destination_id, timestamp=current_time)
                pulsar.queued_jobs += db_dict[galaxy_name][destination_id]["queued"]
                pulsar.running_jobs += db_dict[galaxy_name][destination_id]["running"]
                pulsar.save()
            except History.DoesNotExist:
                History.objects.create(
                    name=destination_id,
                    galaxy=galaxy_name,
                    queued_jobs=db_dict[galaxy_name][destination_id]["queued"],
                    running_jobs=db_dict[galaxy_name][destination_id]["running"],
                    timestamp=current_time
                )
    logger.info("History db updated.")
