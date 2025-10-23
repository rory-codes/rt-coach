from django.urls import path
from . import views

app_name = "fitness_data"

urlpatterns = [
    path("", views.about_me, name="fitness_page"),
]
