from django.http import JsonResponse
from django.shortcuts import render
from core.models import Pulsar, History
from collections import defaultdict
from django.http import JsonResponse
from django.db.models.functions import Trunc, RowNumber, TruncMinute
from django.db.models import OuterRef, Subquery, Avg, Min, Count, Q, F, Window, ExpressionWrapper, IntegerField, FloatField
from django.db.models.expressions import RawSQL
from django.utils import timezone
from datetime import timedelta
import logging
import threading

logger = logging.getLogger('django')

def index(request):
    logger.info(f'thread {threading.current_thread().name} is preparing index')
    context = {'pulsars': list(Pulsar.objects.values('name', 'galaxy', 'latitude', 'longitude', 'queued_jobs', 'running_jobs', 'failed_jobs'))}
    logger.info(f'thread {threading.current_thread().name} returns index')
    return render(request, 'index.html', context)


def pulsar_positions(request):
    logger.info(f'thread {threading.current_thread().name} is preparing pulsar positions')
    response = JsonResponse(
        {'pulsars': list(Pulsar.objects.values('name', 'galaxy', 'latitude', 'longitude', 'queued_jobs', 'running_jobs', 'failed_jobs'))}
    )
    logger.info(f'thread {threading.current_thread().name} returns pulsar positions')
    return response

def play_history(request, history_range, history_window):
    # TODO use history range
    logger.info(f'thread {threading.current_thread().name} is preparing play history')
    now = timezone.now()
    if history_window == "minute":
        history_objects = History.objects.filter(timestamp__gte=(now - timedelta(minutes=10)))
    elif history_window == "hour":
        history_objects = History.objects.filter(timestamp__gte=(now - timedelta(hours=1)), timestamp__second__gte=30)
    elif history_window == "day":
        history_objects = History.objects.filter(timestamp__gte=(now - timedelta(days=1)), timestamp__minute__gte=30)
    else:
        logger.critical("bad history window request")
        return JsonResponse({}, safe=False)
    logger.info(f'thread {threading.current_thread().name} took data from database for play history')
    # Initialize a dictionary to group by timestamp
    grouped_data = defaultdict(list)
    for history in history_objects:
        try:
            pulsar = Pulsar.objects.get(name=history.name, galaxy=history.galaxy)
            entry = {
                'name': history.name,
                'galaxy': history.galaxy,
                'latitude': pulsar.latitude,
                'longitude': pulsar.longitude,
                'queued_jobs': history.queued_jobs,
                'running_jobs': history.running_jobs,
                'failed_jobs': history.failed_jobs,
            }
            timestamp_data = grouped_data[str(history.timestamp.replace(microsecond=0))].append(entry)
        except Pulsar.DoesNotExist:
            logger.info("Pulsar from history: " + history.name + " does not exist anymore!")
    logger.info(f'thread {threading.current_thread().name} returns play history')
    return JsonResponse(grouped_data, safe=False)
