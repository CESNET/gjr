from django.core.management.base import BaseCommand
from core.models import History, HistoryMonth
from django.utils import timezone
from django.db.models import Avg, Count
from datetime import timedelta
from django.db import transaction
import logging

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = (
        "This script takes data from History database of last day queued, running and failed jobs and makes for every destination for every hour average from these metrics and then store it into HistoryMonth database."
    )

    def handle(self, *args, **options):
        logger.info("Handling db_day_to_month request.")

        # Define the timeframe for the last day
        now = timezone.now()
        one_day_ago = now - timedelta(days=1)

        # Delete data older than one day
        History.objects.filter(timestamp__lt=one_day_ago).delete()

        # Query last day's data
        last_day_data = History.objects.all()

        # Calculate hourly averages for each destination
        hourly_averages = (last_day_data
                           .annotate(hour=timezone.localtime('timestamp').hour)
                           .values('name', 'galaxy', 'hour')
                           .annotate(
                               queued_jobs_hour_avg=Avg('queued_jobs'),
                               running_jobs_hour_avg=Avg('running_jobs'),
                               failed_jobs_hour_avg=Avg('failed_jobs'),
                           )
                           .order_by('name', 'hour'))

        # Save the hourly averages to the HistoryMonth model
        with transaction.atomic():
            for record in hourly_averages:
                hour = record['hour']
                # TODO is this allright that it is now? it should be that exact hour in past
                timestamp = now.replace(hour=hour, minute=0, second=0, microsecond=0)

                HistoryMonth.objects.create(
                    name=record['name'],
                    galaxy=record['galaxy'],
                    queued_jobs_hour_avg=record['queued_jobs_hour_avg'],
                    running_jobs_hour_avg=record['running_jobs_hour_avg'],
                    failed_jobs_hour_avg=record['failed_jobs_hour_avg'],
                    timestamp=timestamp,
                )

        logger.info("db_day_to_month operation completed successfully.")
