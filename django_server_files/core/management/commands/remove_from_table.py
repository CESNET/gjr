from django.core.management.base import BaseCommand
from core.models import Pulsar

class Command(BaseCommand):
    help = 'Removes specific pulsars objects from the database'

    def handle(self, *args, **options):
        remove_concrete_pulsar("eu_pbs")
        remove_concrete_pulsar("pulsar_mira_tpv")
        remove_concrete_pulsar("pulsar_sanjay_tpv")
        create_pulsar_eu_pbs()


def remove_pulsars_except_eu_galaxy():
    Pulsar.objects.exclude(galaxy__contains="galaxy.eu").delete()
    print(f"pulsars except galaxy eu were removed")

def remove_concrete_pulsar(name):
    Pulsar.objects.filter(name=name).delete()
    print(f"pulsar was removed")

def create_pulsar_eu_pbs():
    Pulsar.objects.create(
        name="eu_pbs",
        galaxy="usegalaxy.eu",
        latitude=48.012669109891426,
        longitude=7.835061597283835,
        queued_jobs=0,
        running_jobs=0,
        failed_jobs=0
    )
