from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from core.models import HistoryYear, HistoryFinal
from django.db.models import Avg
from django.db.models.functions import ExtractMonth, ExtractYear
import logging

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = 'Aggregate yearly history data into final history data and clean up old records in HistoryYear.'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        one_year_ago = now - timedelta(days=365)

        # Filter for only the last year
        last_year_data = HistoryYear.objects.filter(
            timestamp__gte=one_year_ago,
            timestamp__lt=now
        )

        if not last_year_data.exists():
            logger.info("No HistoryYear data for the last year (%s - %s). Nothing to aggregate.", one_year_ago, now)
            return

        # Monthly aggregation using ExtractMonth and ExtractYear
        monthly_averages = (
            last_year_data
            .annotate(month=ExtractMonth('timestamp'), year=ExtractYear('timestamp'))
            .values('name', 'galaxy', 'month', 'year')
            .annotate(
                queued_jobs_month_avg=Avg('queued_jobs_day_avg'),
                running_jobs_month_avg=Avg('running_jobs_day_avg'),
                failed_jobs_month_avg=Avg('failed_jobs_day_avg')
            )
            .order_by('name', 'galaxy', 'year', 'month')
        )

        created_count = 0
        for record in monthly_averages:
            month = record['month']
            year = record['year']
            timestamp = datetime(year, month, 1, 0, 0, 0, 0, tzinfo=timezone.get_current_timezone())
            HistoryFinal.objects.create(
                name=record['name'],
                galaxy=record['galaxy'],
                queued_jobs_month_avg=int(round(record['queued_jobs_month_avg'] or 0)),
                running_jobs_month_avg=int(round(record['running_jobs_month_avg'] or 0)),
                failed_jobs_month_avg=int(round(record['failed_jobs_month_avg'] or 0)),
                timestamp=timestamp
            )
            created_count += 1

        # Delete data older than one year
        HistoryYear.objects.filter(timestamp__lt=one_year_ago).delete()

        logger.info("Aggregated %d monthly records into HistoryFinal.", created_count)