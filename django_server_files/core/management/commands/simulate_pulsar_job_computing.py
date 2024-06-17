import random
import time
from django.core.management.base import BaseCommand
from core.models import Pulsar

class Command(BaseCommand):
    help = 'Simulate pulsar job computing'

    def handle(self, *args, **options):
        # Define the range of job_num variation
        job_num_var = 10

        while True:
            print("Pulsar job number updating...")

            for pulsar in Pulsar.objects.all():
                job_num_change = random.randint(-job_num_var, job_num_var)
                pulsar.job_num = pulsar.job_num + job_num_change if pulsar.job_num + job_num_change >= 0 else 0
                pulsar.save()

            time.sleep(2)
