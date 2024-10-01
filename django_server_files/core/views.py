from django.http import JsonResponse
from django.shortcuts import render
from core.models import Pulsar, History
from collections import defaultdict

# Create your views here.

def index(request):
    context = {'pulsars': list(Pulsar.objects.values('name', 'galaxy', 'latitude', 'longitude', 'queued_jobs', 'running_jobs', 'failed_jobs'))}
    return render(request, 'index.html', context)


def pulsar_positions(request):
    return JsonResponse(
        {'pulsars': list(Pulsar.objects.values('name', 'galaxy', 'latitude', 'longitude', 'queued_jobs', 'running_jobs', 'failed_jobs'))}
    )

def play_history(request, history_range):
    # Query all History objects and order them by timestamp
    # history_objects = History.objects.all().order_by('timestamp')
    # ordering is maybe useless because theay are already ordered by timestamp
    history_objects = History.objects.all()

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

            if not any(e['name'] == entry['name'] and e['galaxy'] == entry['galaxy'] for e in timestamp_data):
                timestamp_data.append(entry)
        except Pulsar.DoesNotExist:
            # TODO handle error
            # print("Pulsar from history does not exist!", history.name)
            error = "Pulsar from history does not exist!"

    # Convert the defaultdict to a regular dictionary for JSON serialization
    data = {timestamp: entries for timestamp, entries in grouped_data.items()}
    return JsonResponse(data, safe=False)

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
