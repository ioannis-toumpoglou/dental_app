from django.urls import path, include

from . import views

urlpatterns = [
    path('calendar/', views.calendar_data, name='calendar')
]
