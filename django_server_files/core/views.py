from django.http import JsonResponse
from django.shortcuts import render
from core.models import Pulsar, History
from collections import defaultdict
from django.http import JsonResponse
from django.db.models.functions import Trunc, RowNumber
from django.db.models import OuterRef, Subquery, Avg, Min, Count, Q, F, Window, ExpressionWrapper, IntegerField, FloatField
from django.db.models.expressions import RawSQL

# Create your views here.

def index(request):
    context = {'pulsars': list(Pulsar.objects.values('name', 'galaxy', 'latitude', 'longitude', 'queued_jobs', 'running_jobs', 'failed_jobs'))}
    return render(request, 'index.html', context)


def pulsar_positions(request):
    return JsonResponse(
        {'pulsars': list(Pulsar.objects.values('name', 'galaxy', 'latitude', 'longitude', 'queued_jobs', 'running_jobs', 'failed_jobs'))}
    )

"""
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
"""

"""
def play_history(request, history_range):
    result_count = 100
    history_data = History.objects.all()
    total_count = history_data.count()
    result_start = round((history_range / result_count) * total_count)

    # Apply raw SQL for safer window function: row numbers
    raw_sql = 'ROW_NUMBER() OVER (ORDER BY timestamp ASC)'
    history_with_row_number = history_data.annotate(
        row_number=RawSQL(raw_sql, ())
    )

    # Prepare the reduced dataset from which a sample will be drawn
    reduced_data = history_with_row_number[result_start:]

    # Aggregation per time group based on available row numbers
    sliced_count = total_count - result_start
    aggregated_data = reduced_data.annotate(
        time_group=ExpressionWrapper(
            ((F('row_number') - 1) * result_count) / sliced_count,
            output_field=FloatField()
        )
    ).values(
        'time_group', 'name', 'galaxy'
    ).annotate(
        aggregated_timestamp=Min('timestamp'),  # Min timestamp in each group
        avg_queued_jobs=Avg('queued_jobs'),
        avg_running_jobs=Avg('running_jobs'),
        avg_failed_jobs=Avg('failed_jobs'),
        latitude=Subquery(
            Pulsar.objects.filter(name=OuterRef('name'), galaxy=OuterRef('galaxy'))
            .values('latitude')[:1]
        ),
        longitude=Subquery(
            Pulsar.objects.filter(name=OuterRef('name'), galaxy=OuterRef('galaxy'))
            .values('longitude')[:1]
        )
    ).values(
        'aggregated_timestamp', 'name', 'galaxy', 'latitude', 'longitude', 'avg_queued_jobs', 'avg_running_jobs', 'avg_failed_jobs'
    )

    # Preparing response
    grouped_data = defaultdict(list)
    for entry in aggregated_data:
        data_point = {
            'name': entry['name'],
            'galaxy': entry['galaxy'],
            'latitude': entry['latitude'],
            'longitude': entry['longitude'],
            'queued_jobs': entry['avg_queued_jobs'],
            'running_jobs': entry['avg_running_jobs'],
            'failed_jobs': entry['avg_failed_jobs'],
        }
        key = str(entry['aggregated_timestamp'])
        grouped_data[key].append(data_point)

    return JsonResponse(dict(grouped_data), safe=False)
"""


def play_history(request, history_range):
    # Query all History objects and order them by timestamp
    # history_objects = History.objects.all().order_by('timestamp')
    # ordering is maybe useless because theay are already ordered by timestamp

    history_objects = History.objects.all()[:1000]

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

            # if not any(e['name'] == entry['name'] and e['galaxy'] ==  entry['galaxy'] for e in timestamp_data):
            #     timestamp_data.append(entry)

            if not any(e['name'] == entry['name'] and e['galaxy'] ==  entry['galaxy'] for e in timestamp_data):
                 timestamp_data.append(entry)
            """
            else:
                for e in timestamp_data:
                    if e['name'] == entry['name'] and e['galaxy'] ==  entry['galaxy']:
                        e['queued_jobs'] = (e['queued_jobs'] + entry['queued_jobs']) / 2
                        e['running_jobs'] = (e['running_jobs'] + entry['running_jobs']) / 2
                        e['failed_jobs'] = (e['failed_jobs'] + entry['failed_jobs']) / 2
            """
        except Pulsar.DoesNotExist:
            # TODO handle error
            # print("Pulsar from history does not exist!", history.name)
            error = "Pulsar from history does not exist!"

    # Convert the defaultdict to a regular dictionary for JSON serialization
    # data = {timestamp: entries for timestamp, entries in grouped_data.items()}
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
