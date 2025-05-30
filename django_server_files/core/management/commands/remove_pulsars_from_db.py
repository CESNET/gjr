from django.core.management.base import BaseCommand
from core.models import Pulsar

class Command(BaseCommand):
    help = 'Removes specific pulsars objects from the database'

    def handle(self, *args, **options):
        remove_pulsars()

def remove_pulsars():
    Pulsar.objects.all().delete()
    print(f"pulsars were removed")
