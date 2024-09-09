from django.core.management.base import BaseCommand
from myapp.models import Pulsar, History
from django.utils import timezone

class Command(BaseCommand):
    help = 'Store history of Pulsar table'

    def handle(self, *args, **kwargs):
        while True:
            current_time = timezone.now()
            pulsars = Pulsar.objects.all()

            for pulsar in pulsars:
                History.objects.create(
                    pulsar=pulsar,
                    name=pulsar.name,
                    galaxy=pulsar.galaxy,
                    queued_jobs=pulsar.queued_jobs,
                    running_jobs=pulsar.running_jobs,
                    failed_jobs=pulsar.failed_jobs,
                    timestamp=current_time
                )

            self.stdout.write(self.style.SUCCESS('Successfully stored history'))

            time.sleep(5)
