from django.test import TestCase
from django.utils import timezone
from core.models import (
    Galaxy,
    Pulsar,
    PulsarLongestJobs,
    PulsarMostUsedTools,
    PulsarActiveUsers,
    History,
    HistoryMonth,
    HistoryYear,
    HistoryFinal,
    ScheduleStats
)
import datetime

class GalaxyModelTest(TestCase):

    def test_galaxy_creation(self):
        galaxy = Galaxy.objects.create(name='Andromeda', latitude=1.23, longitude=4.56)
        self.assertEqual(galaxy.name, 'Andromeda')
        self.assertEqual(galaxy.latitude, 1.23)
        self.assertEqual(galaxy.longitude, 4.56)

class PulsarModelTest(TestCase):

    def test_pulsar_creation(self):
        pulsar = Pulsar.objects.create(
            name='PulsarX',
            galaxy='Andromeda',
            latitude=1.11,
            longitude=2.22,
            queued_jobs=5,
            running_jobs=10,
            failed_jobs=1,
            anonymous_jobs=3,
            unique_users=4
        )
        self.assertEqual(pulsar.name, 'PulsarX')
        self.assertEqual(pulsar.galaxy, 'Andromeda')
        self.assertEqual(pulsar.latitude, 1.11)
        self.assertEqual(pulsar.longitude, 2.22)
        self.assertEqual(pulsar.queued_jobs, 5)

class PulsarLongestJobsModelTest(TestCase):

    def test_longest_job_assignment(self):
        pulsar = Pulsar.objects.create(name='PulsarY', galaxy='Milky Way')
        longest_job = PulsarLongestJobs.objects.create(pulsar=pulsar, tool='ToolA', hours=5)
        self.assertEqual(longest_job.pulsar, pulsar)
        self.assertEqual(longest_job.tool, 'ToolA')
        self.assertEqual(longest_job.hours, 5)

class PulsarMostUsedToolsModelTest(TestCase):

    def test_most_used_tool_assignment(self):
        pulsar = Pulsar.objects.create(name='PulsarY', galaxy='Milky Way')
        most_used_tool = PulsarMostUsedTools.objects.create(pulsar=pulsar, tool='ToolB', job_num=15)
        self.assertEqual(most_used_tool.pulsar, pulsar)
        self.assertEqual(most_used_tool.tool, 'ToolB')
        self.assertEqual(most_used_tool.job_num, 15)

class PulsarActiveUsersModelTest(TestCase):

    def test_active_users_assignment(self):
        pulsar = Pulsar.objects.create(name='PulsarZ', galaxy='Milky Way')
        active_user = PulsarActiveUsers.objects.create(pulsar=pulsar, user_id='User123', job_num=6)
        self.assertEqual(active_user.pulsar, pulsar)
        self.assertEqual(active_user.user_id, 'User123')
        self.assertEqual(active_user.job_num, 6)

class HistoryModelTest(TestCase):

    def test_history_creation(self):
        timestamp = timezone.now()
        history = History.objects.create(
            name='PulsarX',
            galaxy='Andromeda',
            queued_jobs=8,
            running_jobs=2,
            failed_jobs=0,
            timestamp=timestamp
        )
        self.assertEqual(history.name, 'PulsarX')
        self.assertEqual(history.queued_jobs, 8)
        self.assertEqual(history.timestamp, timestamp)

class HistoryMonthModelTest(TestCase):

    def test_history_month_creation(self):
        timestamp = timezone.now()
        history_month = HistoryMonth.objects.create(
            name='PulsarY',
            galaxy='Milky Way',
            queued_jobs_hour_avg=20,
            running_jobs_hour_avg=10,
            failed_jobs_hour_avg=2,
            timestamp=timestamp
        )
        self.assertEqual(history_month.name, 'PulsarY')
        self.assertEqual(history_month.queued_jobs_hour_avg, 20)

class HistoryYearModelTest(TestCase):

    def test_history_year_creation(self):
        timestamp = timezone.now()
        history_year = HistoryYear.objects.create(
            name='PulsarZ',
            galaxy='Milky Way',
            queued_jobs_day_avg=100,
            running_jobs_day_avg=50,
            failed_jobs_day_avg=5,
            timestamp=timestamp
        )
        self.assertEqual(history_year.name, 'PulsarZ')
        self.assertEqual(history_year.queued_jobs_day_avg, 100)

class HistoryFinalModelTest(TestCase):

    def test_history_final_creation(self):
        timestamp = timezone.now()
        history_final = HistoryFinal.objects.create(
            name='PulsarQ',
            galaxy='Andromeda',
            queued_jobs_month_avg=500,
            running_jobs_month_avg=250,
            failed_jobs_month_avg=20,
            timestamp=timestamp
        )
        self.assertEqual(history_final.name, 'PulsarQ')
        self.assertEqual(history_final.queued_jobs_month_avg, 500)

class ScheduleStatsModelTest(TestCase):

    def test_schedule_stats_creation(self):
        timestamp = timezone.now()
        schedule_stat = ScheduleStats.objects.create(
            dest_id='PulsarX',
            timestamp=timestamp,
            mean_slowndown=1.0,
            bounded_slowndown=1.5,
            response_time=2.0
        )
        self.assertEqual(schedule_stat.dest_id, 'PulsarX')
        self.assertEqual(schedule_stat.mean_slowndown, 1.0)
        self.assertEqual(schedule_stat.bounded_slowndown, 1.5)
        self.assertEqual(schedule_stat.response_time, 2.0)
