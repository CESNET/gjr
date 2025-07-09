from django.core.management.base import BaseCommand
from core.models import History, HistoryMonth
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
from django.db.models.functions import ExtractHour
import logging

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = "Aggregate the last day's History records into hourly averages in HistoryMonth"

    def handle(self, *args, **options):
        # Set your time window for the last full day (e.g., 24 hours ago up to now)
        now = timezone.now()
        one_day_ago = now - timedelta(days=1)

        # FILTER FOR ONLY THE LAST DAY
        last_day_data = History.objects.filter(
            timestamp__gte=one_day_ago,
            timestamp__lt=now
        )

        if not last_day_data.exists():
            logger.info("No History data for the last day (%s - %s). Nothing to aggregate.", one_day_ago, now)
            return

        # HOURLY AGGREGATION USING ExtractHour
        hourly_averages = (
            last_day_data
            .annotate(hour=ExtractHour('timestamp'))
            .values('name', 'galaxy', 'hour')
            .annotate(
                queued_jobs_hour_avg=Avg('queued_jobs'),
                running_jobs_hour_avg=Avg('running_jobs'),
                failed_jobs_hour_avg=Avg('failed_jobs'),
            )
            .order_by('name', 'galaxy', 'hour')
        )

        created_count = 0
        # SAVE TO HistoryMonth
        for record in hourly_averages:
            hour = record['hour']
            timestamp = one_day_ago.replace(hour=hour, minute=0, second=0, microsecond=0)
            obj = HistoryMonth.objects.create(
                name=record['name'],
                galaxy=record['galaxy'],
                queued_jobs_hour_avg=int(round(record['queued_jobs_hour_avg'] or 0)),
                running_jobs_hour_avg=int(round(record['running_jobs_hour_avg'] or 0)),
                failed_jobs_hour_avg=int(round(record['failed_jobs_hour_avg'] or 0)),
                timestamp=timestamp,
            )
            created_count += 1

        # Delete data older than one day
        History.objects.filter(timestamp__lt=one_day_ago).delete()

        logger.info("Aggregated %d hourly records into HistoryMonth.", created_count)
