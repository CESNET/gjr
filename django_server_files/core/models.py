from django.db import models

# Create your models here.
# class Pulsar(models.Model):
#     name = models.CharField(max_length=10)
#     latitude = models.FloatField()
#     longitude = models.FloatField()
#     job_num = models.IntegerField()

class Pulsar(models.Model):
    name = models.CharField(max_length=20)
    galaxy = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    queued_jobs = models.IntegerField()
    running_jobs = models.IntegerField()
    failed_jobs = models.IntegerField()

# add models for galaxy servers and runners
