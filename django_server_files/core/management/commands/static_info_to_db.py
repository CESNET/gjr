import random
import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Pulsar, Galaxy

class Command(BaseCommand):
    help = 'Generates pulsar and galaxy objects in the database from static user files'

    def handle(self, *args, **options):
        galaxies_path = os.path.join(settings.BASE_DIR, 'static', 'db_static_data', 'galaxies.txt')

        if not os.path.exists(galaxies_path):
            self.stdout.write(self.style.ERROR(f"File does not exist: {galaxies_path}"))
            return

        with open(galaxies_path, mode='r', newline='\n', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')

            for row in reader:
                name = row['name']
                latitude = float(row['lat'])
                longitude = float(row['long'])

                self.add_galaxy_server(name, latitude, longitude)

            self.stdout.write(self.style.SUCCESS(f"Successfully added galaxies from {galaxies_path}"))

        pulsars_path = os.path.join(settings.BASE_DIR, 'static', 'db_static_data', 'pulsars.txt')

        if not os.path.exists(pulsars_path):
            self.stdout.write(self.style.ERROR(f"File does not exist: {pulsars_path}"))
            return

        with open(pulsars_path, mode='r', newline='\n', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')

            for row in reader:
                galaxy_name = row['galaxy']
                pulsar_id = row['pulsar_id']
                latitude = float(row['lat'])
                longitude = float(row['long'])
                description = row['desc']

                # add pulsar if it does not exist
                self.add_pulsar(galaxy_name, pulsar_id, latitude, longitude, description)

            self.stdout.write(self.style.SUCCESS(f"Successfully added pulsars from {pulsars_path}"))

    def add_galaxy_server(self, galaxy_name, latitude, longitude):
        _, created = Galaxy.objects.get_or_create(
            name=galaxy_name,
            latitude=latitude,
            longitude=longitude
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created galaxy: {galaxy_name}"))
        else:
            self.stdout.write(self.style.WARNING(f"Galaxy already exists: {galaxy_name}"))

    def add_pulsar(self, galaxy_name, pulsar_id, latitude, longitude, description):
        _, created = Pulsar.objects.get_or_create(
            name=pulsar_id,
            galaxy=galaxy_name,
            latitude=latitude,
            longitude=longitude,
            queued_jobs=0,
            running_jobs=0,
            failed_jobs=0
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created pulsar: {pulsar_id}"))
        else:
            self.stdout.write(self.style.WARNING(f"Pulsar already exists: {pulsar_id}"))
