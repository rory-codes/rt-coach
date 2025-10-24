# workout/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.new_plan, name="new_plan"),
    path("plan/<int:pk>/", views.plan_detail, name="plan_detail"),
    path("plan/<int:pk>/export.csv", views.export_plan_csv, name="export_plan_csv"),
]
