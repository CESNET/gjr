from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pulsar-positions/', views.pulsar_positions, name='pulsar-positions/'),
    path('play-history/<int:history_range>/', views.play_history, name='play-history/'),
    path('show-history-moment/<int:history_range>/', views.show_history_moment, name='show-history-moment/'),
]
