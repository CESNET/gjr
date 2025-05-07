from django.db import models
from django.utils import timezone

class Galaxy(models.Model):
    name = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()

# live pulsar stats

class Pulsar(models.Model):
    name = models.CharField(max_length=20)
    galaxy = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    queued_jobs = models.IntegerField(null=False, default=0)
    running_jobs = models.IntegerField(null=False, default=0)
    failed_jobs = models.IntegerField(null=False, default=0)
    anonymous_jobs = models.IntegerField(null=False, default=0)
    unique_users = models.IntegerField(null=False, default=0)

class PulsarLongestJobs(models.Model):
    pulsar = models.ForeignKey('Pulsar', on_delete=models.CASCADE, related_name='longestjobs', null=True, blank=True)
    tool = models.CharField(max_length=100)
    hours = models.IntegerField()

class PulsarMostUsedTools(models.Model):
    pulsar = models.ForeignKey('Pulsar', on_delete=models.CASCADE, related_name='mostusedtools', null=True, blank=True)
    tool = models.CharField(max_length=100)
    job_num = models.IntegerField()

class PulsarActiveUsers(models.Model):
    pulsar = models.ForeignKey('Pulsar', on_delete=models.CASCADE, related_name='activeusers', null=True, blank=True)
    user_id = models.CharField(max_length=50)
    job_num = models.IntegerField()

# history

class History(models.Model):
    name = models.CharField(max_length=20)
    galaxy = models.CharField(max_length=20)
    queued_jobs = models.IntegerField(default=0)
    running_jobs = models.IntegerField(default=0)
    failed_jobs = models.IntegerField(default=0)
    timestamp = models.DateTimeField()

class HistoryMonth(models.Model):
    name = models.CharField(max_length=20)
    galaxy = models.CharField(max_length=20)
    queued_jobs_hour_avg = models.IntegerField(default=0)
    running_jobs_hour_avg = models.IntegerField(default=0)
    failed_jobs_hour_avg = models.IntegerField(default=0)
    timestamp = models.DateTimeField()

class HistoryYear(models.Model):
    name = models.CharField(max_length=20)
    galaxy = models.CharField(max_length=20)
    queued_jobs_day_avg = models.IntegerField(default=0)
    running_jobs_day_avg = models.IntegerField(default=0)
    failed_jobs_day_avg = models.IntegerField(default=0)
    timestamp = models.DateTimeField()

class HistoryFinal(models.Model):
    name = models.CharField(max_length=20)
    galaxy = models.CharField(max_length=20)
    queued_jobs_month_avg = models.IntegerField(default=0)
    running_jobs_month_avg = models.IntegerField(default=0)
    failed_jobs_month_avg = models.IntegerField(default=0)
    timestamp = models.DateTimeField()

# schedulling

# class ScheduleStats(models.Model):
#     job_id = models.CharField(max_length=20)
#     dest_id = models.CharField(max_length=20)
#     release = models.DateTimeField()
#     start = models.DateTimeField()
#     end = models.DateTimeField()

class ScheduleStats(models.Model):
    dest_id = models.CharField(max_length=20)
    timestamp = models.DateTimeField(default=timezone.now)
    mean_slowndown = models.FloatField(default=0.0)
    bounded_slowndown = models.FloatField(default=0.0)
    response_time = models.FloatField(default=0.0)
