import random
import time
from django.core.management.base import BaseCommand
from core.models import Pulsar

class Command(BaseCommand):
    help = 'Simulate pulsar job computing'

    def handle(self, *args, **options):
        # Define the range of job_num variation
        queued_num_var = 9
        running_num_var = 5
        failed_num_var = 3

        self.inicialize_simulation()

        while True:
            self.stdout.write(self.style.SUCCESS('Successfully simulated pulsar computation.'))

            for pulsar in Pulsar.objects.all():
                pulsar.queued_jobs = self.update_pulsar(pulsar.queued_jobs, queued_num_var)
                pulsar.running_jobs = self.update_pulsar(pulsar.running_jobs, running_num_var)
                pulsar.failed_jobs = self.update_pulsar(pulsar.failed_jobs, failed_num_var)
                pulsar.save()

            time.sleep(3.5)

    def update_pulsar(self, metric_to_update, metric_variance):
        job_num_change = random.randint(-(metric_variance+1), metric_variance)
        return metric_to_update + job_num_change if metric_to_update + job_num_change >= 0 else 0

    def inicialize_simulation(self):
        for pulsar in Pulsar.objects.all():
                pulsar.queued_jobs = random.randint(30, 70)
                pulsar.running_jobs = random.randint(15, 30)
                pulsar.failed_jobs = random.randint(8, 15)
                pulsar.save()
