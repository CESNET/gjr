# Generated by Django 4.2.4 on 2024-04-29 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='name',
            field=models.CharField(max_length=10),
        ),
    ]
