from django.db import models

# Create your models here.
class Pulsar(models.Model):
    name = models.CharField(max_length=10)
    latitude = models.FloatField()
    longitude = models.FloatField()
    job_num = models.IntegerField()

# add models for galaxy servers and runners
