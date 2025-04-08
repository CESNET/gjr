from django.test import TestCase, Client
from django.urls import reverse
from core.models import Pulsar

class ViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
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

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PulsarZ")

    def test_pulsar_positions_view(self):
        response = self.client.get(reverse('pulsar_positions'))
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIn('PulsarZ', [p['name'] for p in response_json['pulsars']])
