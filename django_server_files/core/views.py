from django.http import JsonResponse
from django.shortcuts import render
from core.models import Pulsar

# Create your views here.
def index(request):
    context = {'pulsars': list(Pulsar.objects.values('name', 'galaxy', 'latitude', 'longitude', 'queued_jobs', 'running_jobs', 'failed_jobs'))}
    return render(request, 'index.html', context)


def pulsar_positions(request):
    return JsonResponse(
        {'pulsars': list(Pulsar.objects.values('name', 'galaxy', 'latitude', 'longitude', 'queued_jobs', 'running_jobs', 'failed_jobs'))}
    )
