from django.core.management.base import BaseCommand
from django.db.models import Avg
from django.utils import timezone
from myapp.models import History, HistoryMonth, HistoryYear, HistoryFinal
from django.db.models.functions import TruncHour, TruncDay, TruncMonth

class Command(BaseCommand):
    help = 'Aggregate data from History table to HistoryMonth, HistoryYear, and HistoryFinal'

    def handle(self, *args, **options):
        # Aggregate data by hour
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

        self.stdout.write(self.style.SUCCESS('Successfully aggregated by hour into HistoryMonth'))

        # Aggregate data by day
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

        self.stdout.write(self.style.SUCCESS('Successfully aggregated by day into HistoryYear'))

        # Aggregate data by month
        month_aggregates = History.objects.annotate(month=TruncMonth('timestamp')).values('name', 'galaxy', 'month').annotate(
            queued_jobs_month_avg=Avg('queued_jobs'),
            running_jobs_month_avg=Avg('running_jobs'),
            failed_jobs_month_avg=Avg('failed_jobs')
        )

        for aggregate in month_aggregates:
            HistoryFinal.objects.create(
                name=aggregate['name'],
                galaxy=aggregate['galaxy'],
                queued_jobs_month_avg=aggregate['queued_jobs_month_avg'],
                running_jobs_month_avg=aggregate['running_jobs_month_avg'],
                failed_jobs_month_avg=aggregate['failed_jobs_month_avg'],
                timestamp=aggregate['month']
            )

        self.stdout.write(self.style.SUCCESS('Successfully aggregated by month into HistoryFinal'))
