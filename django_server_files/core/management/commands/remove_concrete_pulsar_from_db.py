from django.core.management.base import BaseCommand
from core.models import Pulsar

class Command(BaseCommand):
    help = 'Removes specific pulsar objects from the database'

    def add_arguments(self, parser):
        # Add argument to specify pulsar name
        parser.add_argument('pulsar_name', type=str, help='The name of the pulsar to be removed')

    def handle(self, *args, **options):
        pulsar_name = options['pulsar_name']
        remove_concrete_pulsar(pulsar_name)

def remove_concrete_pulsar(name):
    if Pulsar.objects.filter(name=name).exists():
        Pulsar.objects.filter(name=name).delete()
        print(f"Pulsar {name} was removed")
    else:
        print(f"No pulsar named {name} found")
