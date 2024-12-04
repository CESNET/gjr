from django.core.management.base import BaseCommand
from core.models import Pulsar

class Command(BaseCommand):
    help = 'Removes specific pulsars objects from the database'

    def handle(self, *args, **options):
        remove_pulsars_except_eu_galaxy()

def remove_pulsars_except_eu_galaxy():
    Pulsar.objects.exclude(galaxy__contains="galaxy.eu").delete()
    print(f"pulsars except galaxy eu were removed")
