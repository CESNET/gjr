from django.core.management.base import BaseCommand
from core.models import History, HistoryMonth, HistoryYear
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
from django.db.models.functions import TruncHour, TruncDay
import logging

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = (
        "This script takes data from History database of last day queued, "
        "running and failed jobs and makes for every destination for every "
        "hour average from these metrics and then store it into HistoryMonth "
        "database and for the last day average and then store it into HistoryYear database."
    )

    def handle(self, *args, **options):
        logger.info("Handling store_db_history request.")
        # Define the timeframe for the last day
        now = timezone.now()
        one_day_ago = now - timedelta(days=1)
        # Delete data older than one day
        History.objects.filter(timestamp__lt=one_day_ago).delete()
        
        # Aggregate data by hour to month db
        hour_aggregates = History.objects.annotate(hour=TruncHour('timestamp')).values('name', 'galaxy', 'hour').annotate(
            queued_jobs_hour_avg=Avg('queued_jobs'),
            running_jobs_hour_avg=Avg('running_jobs'),
            failed_jobs_hour_avg=Avg('failed_jobs')
        )
        for aggregate in hour_aggregates:
            HistoryMonth.objects.create(
                name=aggregate['name'],
                galaxy=aggregate['galaxy'],
                queued_jobs_hour_avg=aggregate['queued_jobs_hour_avg'],
                running_jobs_hour_avg=aggregate['running_jobs_hour_avg'],
                failed_jobs_hour_avg=aggregate['failed_jobs_hour_avg'],
                timestamp=aggregate['hour']
            )
        
        # Aggregate data by day to year db
        day_aggregates = History.objects.annotate(day=TruncDay('timestamp')).values('name', 'galaxy', 'day').annotate(
            queued_jobs_day_avg=Avg('queued_jobs'),
            running_jobs_day_avg=Avg('running_jobs'),
            failed_jobs_day_avg=Avg('failed_jobs')
        )

        for aggregate in day_aggregates:
            HistoryYear.objects.create(
                name=aggregate['name'],
                galaxy=aggregate['galaxy'],
                queued_jobs_day_avg=aggregate['queued_jobs_day_avg'],
                running_jobs_day_avg=aggregate['running_jobs_day_avg'],
                failed_jobs_day_avg=aggregate['failed_jobs_day_avg'],
                timestamp=aggregate['day']
            )

        logger.info("tore_db_history operation completed successfully.")
