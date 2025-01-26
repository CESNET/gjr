from django.db import models

# Create your models here.

class Pulsar(models.Model):
    name = models.CharField(max_length=20)
    galaxy = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    queued_jobs = models.IntegerField()
    running_jobs = models.IntegerField()
    failed_jobs = models.IntegerField()

# add models for galaxy servers?

class History(models.Model):
    name = models.CharField(max_length=20)
    galaxy = models.CharField(max_length=20)
    queued_jobs = models.IntegerField()
    running_jobs = models.IntegerField()
    failed_jobs = models.IntegerField()
    timestamp = models.DateTimeField()

class RRDPulsar(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rrd_path = models.CharField(max_length=255)

    def __str__(self):
        return self.name
