from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import HistoryMonth, HistoryYear
from django.db.models import Avg
from django.db.models.functions import ExtractDay
import logging

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = 'Aggregate monthly history data into yearly history data and clean up old records from HistoryMonth'

    def handle(self, *args, **kwargs):
        # Set your time window for the last month
        now = timezone.now()
        one_month_ago = now - timedelta(days=30)

        # Filter for only the last month
        last_month_data = HistoryMonth.objects.filter(
            timestamp__gte=one_month_ago,
            timestamp__lt=now
        )

        if not last_month_data.exists():
            logger.info("No HistoryMonth data for the last month (%s - %s). Nothing to aggregate.", one_month_ago, now)
            return

        # Daily aggregation using ExtractDay
        daily_averages = (
            last_month_data
            .annotate(day=ExtractDay('timestamp'))
            .values('name', 'galaxy', 'day')
            .annotate(
                queued_jobs_day_avg=Avg('queued_jobs_hour_avg'),
                running_jobs_day_avg=Avg('running_jobs_hour_avg'),
                failed_jobs_day_avg=Avg('failed_jobs_hour_avg'),
            )
            .order_by('name', 'galaxy', 'day')
        )

        created_count = 0
        # Save to HistoryYear
        for record in daily_averages:
            day = record['day']
            timestamp = one_month_ago.replace(day=day, hour=0, minute=0, second=0, microsecond=0)
            obj = HistoryYear.objects.create(
                name=record['name'],
                galaxy=record['galaxy'],
                queued_jobs_day_avg=int(round(record['queued_jobs_day_avg'] or 0)),
                running_jobs_day_avg=int(round(record['running_jobs_day_avg'] or 0)),
                failed_jobs_day_avg=int(round(record['failed_jobs_day_avg'] or 0)),
                timestamp=timestamp,
            )
            created_count += 1

        # Delete data older than one month
        HistoryMonth.objects.filter(timestamp__lt=one_month_ago).delete()

        logger.info("Aggregated %d daily records into HistoryYear.", created_count)
