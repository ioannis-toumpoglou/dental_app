from django.urls import path

from . import views

urlpatterns = [
    path('main', views.main, name='main'),
    path('add-patient', views.add_patient, name='add-patient')
]
