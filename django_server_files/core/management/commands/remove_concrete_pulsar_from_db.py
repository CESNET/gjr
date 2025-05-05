from django.core.management.base import BaseCommand
from core.models import Pulsar

class Command(BaseCommand):
    help = 'Removes specific pulsars objects from the database'

    def handle(self, *args, **options):
        remove_concrete_pulsar(args[1])

def remove_concrete_pulsar(name):
    Pulsar.objects.filter(name=name).delete()
    print(f"pulsar {name} was removed")
