from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from core.models import Pulsar, History, Galaxy, PulsarLongestJobs, PulsarMostUsedTools, PulsarActiveUsers, ScheduleStats
from collections import defaultdict
from django.http import JsonResponse
from django.db.models.functions import Trunc, RowNumber, TruncMinute, TruncHour, ExtractMinute, ExtractSecond, Now
from django.db.models import OuterRef, Subquery, Avg, Min, Count, Q, F, Window, ExpressionWrapper, IntegerField, FloatField, DateTimeField, Value, DurationField
from django.db.models.expressions import RawSQL
from django.utils import timezone
import datetime
from datetime import timedelta
import logging
import threading

logger = logging.getLogger('django')

def index(request):
    logger.info(f'thread {threading.current_thread().name} is preparing index')

    # Use the helper function to populate pulsar data
    pulsars_context = get_pulsars_with_related_data()

    # Fetch and prepare galaxy context
    galaxies_context = list(Galaxy.objects.values('name', 'latitude', 'longitude'))

    context = {
        'pulsars_context': pulsars_context,
        'galaxies_context': galaxies_context,
    }

    logger.info(f'thread {threading.current_thread().name} returns index')
    return render(request, 'index.html', context)

def pulsar_positions(request):
    logger.info(f'thread {threading.current_thread().name} is preparing pulsar positions')

    # Use the helper function to get pulsar data
    pulsars_context = get_pulsars_with_related_data()

    response = JsonResponse({'pulsars': pulsars_context})

    logger.info(f'thread {threading.current_thread().name} returns pulsar positions')
    return response

def get_pulsars_with_related_data():
    # Retrieve all pulsars with related data using prefetch_related
    pulsars = Pulsar.objects.prefetch_related('longestjobs', 'mostusedtools', 'activeusers')

    pulsars_context = []
    for pulsar in pulsars:
        pulsar_data = {
            'name': pulsar.name,
            'galaxy': pulsar.galaxy,
            'latitude': pulsar.latitude,
            'longitude': pulsar.longitude,
            'queued_jobs': pulsar.queued_jobs,
            'running_jobs': pulsar.running_jobs,
            'failed_jobs': pulsar.failed_jobs,
            'anonymous_jobs': pulsar.anonymous_jobs,
            'unique_users': pulsar.unique_users,
            'longest_jobs': list(pulsar.longestjobs.values('tool', 'hours')),
            'most_used_tools': list(pulsar.mostusedtools.values('tool', 'job_num')),
            'active_users': list(pulsar.activeusers.values('user_id', 'job_num')),
        }
        pulsars_context.append(pulsar_data)

    return pulsars_context

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
            timestamp__gte=(now - timedelta(days=1) + timedelta(minutes=int((history_range / 100) * 24 * 60)))
        ).annotate(
            truncated=TruncHour('timestamp')
        ).values('truncated', 'name', 'galaxy').annotate(
            average_queued_jobs=Avg('queued_jobs'),
            average_running_jobs=Avg('running_jobs'),
            average_failed_jobs=Avg('failed_jobs')
        )
    elif history_window == "month":
        history_objects = HistoryMonth.objects.filter(
            timestamp__gte=(now - timedelta(days=30) + timedelta(minutes=int((history_range / 100) * 30 * 24 * 60)))
        ).annotate(
            truncated=TruncDay('timestamp')
        ).values('truncated', 'name', 'galaxy').annotate(
            average_queued_jobs=Avg('queued_jobs'),
            average_running_jobs=Avg('running_jobs'),
            average_failed_jobs=Avg('failed_jobs')
        )
    elif history_window == "year":
        history_objects = History.objects.filter(
            timestamp__gte=(now - timedelta(days=365) + timedelta(minutes=int((history_range / 100) * 365 * 24 * 60)))
        ).annotate(
            truncated=TruncMonth('timestamp')
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
                    'queued_jobs': round(history['average_queued_jobs'], 2),
                    'running_jobs': round(history['average_running_jobs'], 2),
                    'failed_jobs': round(history['average_failed_jobs'], 2)
                }
                timestamp_key = str(history['truncated'])
                grouped_data[timestamp_key].append(entry)
            # timestamp_data = grouped_data[str(history.timestamp.replace(microsecond=0))].append(entry)
        except Pulsar.DoesNotExist:
            logger.info("Pulsar from history: " + history['name'] + " does not exist anymore!")

    logger.info(f'thread {threading.current_thread().name} returns play history')
    return JsonResponse(grouped_data, safe=False)

# TODO send also other data like number of its pulsars etc.
def galaxies(request):
    logger.info(f'thread {threading.current_thread().name} is preparing galaxies')
    response = JsonResponse(
        {'galaxies': list(Galaxy.objects.values('name', 'latitude', 'longitude'))}
    )
    logger.info(f'thread {threading.current_thread().name} returns galaxies')
    return response

"""
def compute_slowdowns_and_response(jobs):
    mean_slowdown = []
    bounded_slowdown = []
    response_time = []

    def calculate_mean_slowdown(jobs):
        return sum([1.0 for job in jobs]) / max(1, len(jobs))

    def calculate_bounded_slowdown(jobs):
        return sum([1.0 for job in jobs]) / max(1, len(jobs))

    def calculate_response_time(jobs):
        return sum((job.end - job.start).total_seconds() for job in jobs) / max(1, len(jobs))

    for job_group in jobs:
        mean_slowdown.append(calculate_mean_slowdown(job_group))
        bounded_slowdown.append(calculate_bounded_slowdown(job_group))
        response_time.append(calculate_response_time(job_group))

    return mean_slowdown, bounded_slowdown, response_time

def scheduling_analysis(request, pulsar_name):
    now = timezone.now()
    ten_hours_ago = now - datetime.timedelta(hours=10)

    recent_jobs = ScheduleStats.objects.filter(dest_id=pulsar_name, start__gte=ten_hours_ago)

    interval_stats = []
    for hour in range(0, 10):
        hour_start = ten_hours_ago + datetime.timedelta(hours=hour)
        hour_end = hour_start + datetime.timedelta(hours=1)
        jobs_in_interval = recent_jobs.filter(start__gte=hour_start, start__lt=hour_end)

        if jobs_in_interval.exists():
            interval_stats.append(list(jobs_in_interval))

    # Calculate the stats
    mean_slowdown, bounded_slowdown, response_time = compute_slowdowns_and_response(interval_stats)

    # Construct JSON response
    data = {
        "mean_slowdown": mean_slowdown,
        "bounded_slowdown": bounded_slowdown,
        "response_time": response_time
    }

    return JsonResponse(data, safe=False)
"""

def scheduling_analysis(request, pulsar_name):
    now = timezone.now()
    start = now - datetime.timedelta(days=30)
    stats = ScheduleStats.objects.filter(dest_id=pulsar_name, timestamp__gte=start)
    data = {
        "mean_slowdown": [],
        "bounded_slowdown": [],
        "response_time": []
    }
    for interval in stats:
        interval_timestamp = interval.timestamp
        data["mean_slowdown"].append({
            "date": interval_timestamp,
            "value": interval.mean_slowndown
        })
        data["bounded_slowdown"].append({
            "date": interval_timestamp,
            "value": interval.bounded_slowndown
        })
        data["response_time"].append({
            "date": interval_timestamp,
            "value": interval.response_time
        })
    return JsonResponse(data, safe=False)
