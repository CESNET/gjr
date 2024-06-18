# Generated by Django 4.2.4 on 2024-06-17 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pulsar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('galaxy', models.CharField(max_length=20)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('queued_jobs', models.IntegerField()),
                ('running_jobs', models.IntegerField()),
                ('failed_jobs', models.IntegerField()),
            ],
        ),
    ]
