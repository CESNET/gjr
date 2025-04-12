from django.core.management.base import BaseCommand
from core.models import History, HistoryMonth
import logging
from datetime import timedelta

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = (
        "Takes data from galaxy influx database and distributes them into live view (pulsar database) and history view (history database)."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def handle(self, *args, **options):
        logger.info("Handling update_influx_data request.")
