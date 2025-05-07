from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from core.models import HistoryYear, HistoryFinal
from django.db.models import Avg
import logging

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = 'Aggregate yearly history data into final history data and clean up old records in HistoryYear.'

    def handle(self, *args, **kwargs):
        current_time = timezone.now()
        one_year_ago = current_time - timedelta(days=365)
        logger.info("Aggregating yearly data into monthly averages for final storage...")
        # Extract month and year from timestamp
        yearly_data = (
            HistoryYear.objects.filter(timestamp__gte=one_year_ago)
            .annotate(month=timezone.localtime('timestamp').month, year=timezone.localtime('timestamp').year)
            .values('name', 'galaxy', 'month', 'year')
            .annotate(
                queued_jobs_month_avg=Avg('queued_jobs_day_avg'),
                running_jobs_month_avg=Avg('running_jobs_day_avg'),
                failed_jobs_month_avg=Avg('failed_jobs_day_avg')
            )
        )
        for data in yearly_data:
            # Generate appropriate timestamp for each month
            month_year = datetime(data['year'], data['month'], 1)

            HistoryFinal.objects.create(
                name=data['name'],
                galaxy=data['galaxy'],
                queued_jobs_month_avg=data['queued_jobs_month_avg'],
                running_jobs_month_avg=data['running_jobs_month_avg'],
                failed_jobs_month_avg=data['failed_jobs_month_avg'],
                timestamp=month_year
            )
        logger.info("Deleting old records from HistoryYear...")
        HistoryYear.objects.filter(timestamp__lt=one_year_ago).delete()
        logger.info("Successfully aggregated yearly data into monthly averages and cleaned up old records.")
