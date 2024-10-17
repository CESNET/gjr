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

# Create your views here.

def index(request):
    context = {'pulsars': list(Pulsar.objects.values('name', 'galaxy', 'latitude', 'longitude', 'queued_jobs', 'running_jobs', 'failed_jobs'))}
    return render(request, 'index.html', context)


def pulsar_positions(request):
    return JsonResponse(
        {'pulsars': list(Pulsar.objects.values('name', 'galaxy', 'latitude', 'longitude', 'queued_jobs', 'running_jobs', 'failed_jobs'))}
    )

def play_history(request, history_range, history_window):
    # TODO use history range and handle that it is in bounds

    now = timezone.now()
    if history_window == "hour":
        history_objects = History.objects.filter(timestamp__gte=(now - timedelta(hours=1)))
    elif history_window == "day":
        history_objects = History.objects.filter(timestamp__gte=(now - timedelta(days=1)))
    elif history_window == "month":
        history_objects = History.objects.filter(timestamp__gte=(now - timedelta(weeks=4)), timestamp__minute=0)
    elif history_window == "year":
        history_objects = History.objects.filter(timestamp__gte=(now - timedelta(weeks=48)), timestamp__hour=0, timestamp__minute=0)
    else:
        print("bad history window request")
        return JsonResponse({}, safe=False)

    # Initialize a dictionary to group by timestamp
    grouped_data = defaultdict(list)

    # Populate the dictionary
    # TODO: redo this into SQL so it is quicker and I do not need to go through history lineary multiple time
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
            timestamp_data = grouped_data[str(history.timestamp.replace(microsecond=0, second=0))]
            # TODO: not great -> it also should be done in SQL already so I do not have more same pulsars in one category due to different time frames

            if not any(e['name'] == entry['name'] and e['galaxy'] ==  entry['galaxy'] for e in timestamp_data):
                 timestamp_data.append(entry)

        except Pulsar.DoesNotExist:
            # TODO handle error
            error = "Pulsar from history does not exist!"

    return JsonResponse(grouped_data, safe=False)

def show_history_moment(request, history_range):
    history_object = History.objects.all()

    # Populate the dictionary
    # TODO: redo this into SQL so it is quicker and I do not need to go through history lineary multiple time
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
            timestamp_data = grouped_data[str(history.timestamp.replace(microsecond=0, second=0))]
            # TODO: not great -> it also should be done in SQL already so I do not have more same pulsars in one category due to different time frames

            if not any(e['name'] == entry['name'] and e['galaxy'] == entry['galaxy'] for e in timestamp_data):
                timestamp_data.append(entry)

        except Pulsar.DoesNotExist:
            # TODO handle error
            # print("Pulsar from history does not exist!", history.name)
            error = "Pulsar from history does not exist!"

    # Convert the defaultdict to a regular dictionary for JSON serialization
    data = {timestamp: entries for timestamp, entries in grouped_data.items()}
    return JsonResponse(data, safe=False)
