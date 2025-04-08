from django.test import TestCase
from core.models import Galaxy, Pulsar, PulsarLongestJobs, PulsarMostUsedTools, PulsarActiveUsers

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
        self.assertEqual(pulsar.queued_jobs, 5)

class PulsarLongestJobsModelTest(TestCase):

    def test_longest_job_assignment(self):
        pulsar = Pulsar.objects.create(name='PulsarY', galaxy='Milky Way')
        longest_job = PulsarLongestJobs.objects.create(pulsar=pulsar, tool='ToolA', hours=5)
        self.assertEqual(longest_job.pulsar, pulsar)
        self.assertEqual(longest_job.tool, 'ToolA')
        self.assertEqual(longest_job.hours, 5)
