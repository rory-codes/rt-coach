# workout/views.py
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import PreferenceForm
from .models import WorkoutPlan
from .services import Metrics, build_plan, plan_to_rows, CSV_COLUMNS

# ... your existing new_plan and plan_detail ...

@login_required
def export_plan_csv(request, pk: int):
    wp = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)
    rows = plan_to_rows(wp.plan_json)

    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = f'attachment; filename="workout_plan_{pk}.csv"'
    writer = csv.DictWriter(resp, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    return resp
