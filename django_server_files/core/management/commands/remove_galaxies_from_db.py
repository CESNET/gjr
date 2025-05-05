from django.core.management.base import BaseCommand
from core.models import Pulsar

class Command(BaseCommand):
    help = 'Removes galaxy objects from the database'

    def handle(self, *args, **options):
        remove_galaxies()

def remove_galaxies():
    Galaxy.objects.delete()
    print(f"galaxies were removed")
