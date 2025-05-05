from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from core.models import Pulsar, History, Galaxy, ScheduleStats
import datetime

class ViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        now = timezone.now()

        # Setup Pulsar instance
        self.pulsar = Pulsar.objects.create(
            name="PulsarZ",
            galaxy="Milky Way",
            latitude=1.0,
            longitude=2.0,
            queued_jobs=3,
            running_jobs=2,
            failed_jobs=1,
            anonymous_jobs=0,
            unique_users=1
        )

        # Setup Galaxy instance
        self.galaxy = Galaxy.objects.create(
            name="Milky Way",
            latitude=50.0,
            longitude=100.0
        )

        # Setup History instance
        self.history = History.objects.create(
            name="PulsarZ",
            galaxy="Milky Way",
            timestamp=now,
            queued_jobs=3,
            running_jobs=2,
            failed_jobs=1
        )

        # Setup ScheduleStats instance
        self.schedule_stat = ScheduleStats.objects.create(
            dest_id="PulsarZ",
            timestamp=now - datetime.timedelta(days=5),
            mean_slowndown=1.5,
            bounded_slowndown=2.0,
            response_time=3.5,
        )

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PulsarZ")
        self.assertContains(response, "Milky Way")

    def test_pulsar_positions_view(self):
        response = self.client.get(reverse('pulsar_positions'))
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIn('PulsarZ', [p['name'] for p in response_json['pulsars']])

    def test_play_history_view(self):
        response = self.client.get(reverse('play_history', args=[50, 'minute']))
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertTrue(isinstance(response_json, dict))

    def test_galaxies_view(self):
        response = self.client.get(reverse('galaxies'))
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIn('Milky Way', [g['name'] for g in response_json['galaxies']])

    def test_scheduling_analysis_view(self):
        response = self.client.get(reverse('scheduling_analysis', args=["PulsarZ"]))
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIn('mean_slowdown', response_json)
        self.assertIn('bounded_slowdown', response_json)
        self.assertIn('response_time', response_json)
