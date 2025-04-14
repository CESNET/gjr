from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from pulsars.models import HistoryMonth, HistoryYear
from django.db.models import Avg

class Command(BaseCommand):
    help = 'Aggregate monthly history data into yearly history data and clean up old records from HistoryMonth.'

    def handle(self, *args, **kwargs):
        current_time = timezone.now()
        one_month_ago = current_time - timedelta(days=30)

        # Aggregate data from HistoryMonth to HistoryYear
        self.stdout.write("Aggregating monthly data into daily averages for yearly storage...")

        # Group by each unique day and relevant aggregation
        monthly_data = (
            HistoryMonth.objects.filter(timestamp__gte=one_month_ago)
            .annotate(day=timezone.localtime('timestamp').day, month=timezone.localtime('timestamp').month, year=timezone.localtime('timestamp').year)
            .values('name', 'galaxy', 'day', 'month', 'year')
            .annotate(
                queued_jobs_day_avg=Avg('queued_jobs_hour_avg'),
                running_jobs_day_avg=Avg('running_jobs_hour_avg'),
                failed_jobs_day_avg=Avg('failed_jobs_hour_avg')
            )
        )

        for data in monthly_data:
            # Calculate the start of the day for the timestamp
            start_of_day = datetime(data['year'], data['month'], data['day'])

            # Create a new HistoryYear record with the correct start of day timestamp
            HistoryYear.objects.create(
                name=data['name'],
                galaxy=data['galaxy'],
                queued_jobs_day_avg=data['queued_jobs_day_avg'],
                running_jobs_day_avg=data['running_jobs_day_avg'],
                failed_jobs_day_avg=data['failed_jobs_day_avg'],
                timestamp=start_of_day
            )

        # Delete old records in HistoryMonth
        self.stdout.write("Deleting old records from HistoryMonth...")
        HistoryMonth.objects.filter(timestamp__lt=one_month_ago).delete()

        self.stdout.write(self.style.SUCCESS("Successfully aggregated daily data into yearly records and cleaned up old records."))
