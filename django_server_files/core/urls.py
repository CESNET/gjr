from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pulsar-positions/', views.pulsar_positions, name='pulsar-positions/'),
    path('play-history/', views.play_history, name='play-history/'),
]
