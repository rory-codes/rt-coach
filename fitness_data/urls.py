from . import views
from django.urls import path

urlpatterns = [
    path('', views.fitness_data, name='fitness_data'),
]