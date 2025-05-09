from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pulsar-positions/', views.pulsar_positions, name='pulsar-positions/'),
    path('play-history/<int:history_range>/<str:history_window>/', views.play_history, name='play-history/'),
    path('galaxies/', views.galaxies, name='galaxies/'),
    path('scheduling-analysis/<str:pulsar_name>/', views.scheduling_analysis, name='scheduling-analysis/'),
]
