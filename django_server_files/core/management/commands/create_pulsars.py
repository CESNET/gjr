import random
from django.core.management.base import BaseCommand
from core.models import Pulsar

class Command(BaseCommand):
    help = 'Generates pulsar objects in the database'

    def handle(self, *args, **options):
        # add_random_pulsars()
        add_galaxy_eu()

def add_random_pulsars():
    NUM_PULSARS_TO_GENERATE = 5
    for _ in range(NUM_PULSARS_TO_GENERATE):
        Pulsar.objects.create(
            name="pulsar",
            latitude=random.uniform(40,60),
            longitude=random.uniform(0,15),
            job_num=random.randint(0, 150)
        )
    print(f"{Pulsar.objects.count()} random pulsars now in the database")


def add_galaxy_eu():
    galaxy_eu_pulsars = [
                            ("Freiburg - Mira's pulsar", 48.1731131, 8.9016003),
                            ("Freiburg - Snajay's pulsar", 48.1731131, 9),
                            ("Rennes - GenOuest bioinformatics", 48.1107856, 1.6836897),
                            ("Bari - RECAS", 41.9028, 12.4964),
                            ("Bari - RECAS 2", 42, 12.4964),
                            ("Bari - INFN", 41.9028, 12.6),
                            ("Brussel - VIB", 50.8476, 4.3572),
                            ("Prague - MetaCentrum", 50.0755, 14.4378),
                            ("Bratislava - IISAS", 48.148598, 17.107748),
                            ("Barcelona - BSC-CNS", 40.416775, -3.703790),
                            ("Ankara - TUBITAK ULAKBIM", 39.2233947, 28.7209361),
                            ("Krakow - Cyfronet", 52.237049, 21.017532),
                            ("Herakilon-Crete - HCMR", 35.3369294, 25.1281525)
                        ]
    for pulsar in galaxy_eu_pulsars:
        Pulsar.objects.create(
            name=pulsar[0],
            latitude=pulsar[1],
            longitude=pulsar[2],
            job_num=random.randint(0, 150)
        )
    print(f"{Pulsar.objects.count()} galaxy.eu and its pulsars now in the database")
