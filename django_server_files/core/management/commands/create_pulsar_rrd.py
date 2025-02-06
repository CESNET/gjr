from django.core.management.base import BaseCommand
import rrdtool
import os
import logging

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = 'Create RRD database for new pulsar'

    def add_arguments(self, parser):
        parser.add_argument('pulsar_name', type=str, help='Name of the pulsar')

    def handle(self, *args, **kwargs):
        pulsar_name = kwargs['pulsar_name']
        rrd_path = f'rrd/{pulsar_name}.rrd'  # Path where the RRD file will be stored

        # Define data sources and RRA (Round Robin Archives)
        data_sources = [
            'DS:running_jobs:GAUGE:20:0:U',
            'DS:waiting_jobs:GAUGE:20:0:U',
            'DS:failed_jobs:GAUGE:20:0:U'
        ]

        rra = [
            'RRA:AVERAGE:0.5:1:600',    # Store every data point for 100 minutes
            'RRA:AVERAGE:0.5:6:700',    # Store 10-minute averages for 1 week
            'RRA:AVERAGE:0.5:24:775',   # Store hourly averages for 1 month
            'RRA:AVERAGE:0.5:288:797'   # Store daily averages for multiple years
        ]

        # Create the RRD
        if not os.path.exists(rrd_path):
            rrdtool.create(rrd_path, '--step', '10', *data_sources, *rra)
            self.stdout.write(self.style.SUCCESS(f'Successfully created RRD for {pulsar_name}'))
            logger.info(f'Successfully created RRD for {pulsar_name}')
