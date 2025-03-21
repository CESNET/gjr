from django.http import JsonResponse
from django.shortcuts import render
from core.models import Pulsar, History
from collections import defaultdict
from django.http import JsonResponse
from django.db.models.functions import Trunc, RowNumber, TruncMinute, TruncHour, ExtractMinute, ExtractSecond, Now
from django.db.models import OuterRef, Subquery, Avg, Min, Count, Q, F, Window, ExpressionWrapper, IntegerField, FloatField, DateTimeField, Value, DurationField
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
    logger.info(f'thread {threading.current_thread().name} is preparing play history')
    now = timezone.now()

    if history_window == "minute":
        history_objects = History.objects.filter(
            timestamp__gte=(now - timedelta(minutes=10) + timedelta(minutes=int((history_range / 100) * 10)))
        ).annotate(
            truncated=TruncMinute('timestamp')
        ).values('truncated', 'name', 'galaxy').annotate(
            average_queued_jobs=Avg('queued_jobs'),
            average_running_jobs=Avg('running_jobs'),
            average_failed_jobs=Avg('failed_jobs')
        )
    elif history_window == "hour":
        history_objects = History.objects.filter(
            timestamp__gte=(now - timedelta(hours=1) + timedelta(minutes=int((history_range / 100) * 60)))
        ).annotate(
            truncated=TruncMinute('timestamp')
        ).values('truncated', 'name', 'galaxy').annotate(
            average_queued_jobs=Avg('queued_jobs'),
            average_running_jobs=Avg('running_jobs'),
            average_failed_jobs=Avg('failed_jobs')
        )
    elif history_window == "day":
        history_objects = History.objects.filter(
            timestamp__gte=(now - timedelta(days=1) + timedelta(minutes=int((history_range / 100) * 1440)))
        ).annotate(
            truncated=TruncHour('timestamp')
        ).values('truncated', 'name', 'galaxy').annotate(
            average_queued_jobs=Avg('queued_jobs'),
            average_running_jobs=Avg('running_jobs'),
            average_failed_jobs=Avg('failed_jobs')
        )
    else:
        logger.critical("bad history window request")
        return JsonResponse({}, safe=False)

    logger.info(f'thread {threading.current_thread().name} took data from database for play history')

    # Initialize a dictionary to group by timestamp
    grouped_data = defaultdict(list)
    seen = set()
    for history in history_objects:
        try:
            if (history['truncated'], history['name'], history['galaxy']) not in seen:
                seen.add((history['truncated'], history['name'], history['galaxy']))
                pulsar = Pulsar.objects.get(name=history['name'], galaxy=history['galaxy'])
                entry = {
                    'name': history['name'],
                    'galaxy': history['galaxy'],
                    'latitude': pulsar.latitude,
                    'longitude': pulsar.longitude,
                    'queued_jobs': history['average_queued_jobs'],
                    'running_jobs': history['average_running_jobs'],
                    'failed_jobs': history['average_failed_jobs'],
                }
                timestamp_key = str(history['truncated'])
                grouped_data[timestamp_key].append(entry)
            # timestamp_data = grouped_data[str(history.timestamp.replace(microsecond=0))].append(entry)
        except Pulsar.DoesNotExist:
            logger.info("Pulsar from history: " + history['name'] + " does not exist anymore!")

    logger.info(f'thread {threading.current_thread().name} returns play history')
    return JsonResponse(grouped_data, safe=False)
