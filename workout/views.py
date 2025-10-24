# workout/views.py
import json
import csv
from typing import Dict
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import PreferenceForm
from .models import WorkoutPlan
from .services import Metrics, build_plan, plan_to_rows, CSV_COLUMNS

@login_required
def new_plan(request):
    """
    Shows a simple form (experience, goal). On POST, builds a plan and redirects
    to plan_detail. Hidden fields for age/rhr/tenrm_json are optional.
    """
    if request.method == "POST":
        form = PreferenceForm(request.POST)
        if form.is_valid():
            experience = form.cleaned_data["experience"]
            goal = form.cleaned_data["goal"]
            age = form.cleaned_data.get("age")
            rhr = form.cleaned_data.get("rhr")
            tenrm_json = form.cleaned_data.get("tenrm_json") or "{}"
            try:
                tenrm_map: Dict[str, float] = json.loads(tenrm_json)
            except json.JSONDecodeError:
                tenrm_map = {}

            metrics = Metrics(age=age, rhr=rhr, tenrm=tenrm_map)
            plan = build_plan(experience, goal, metrics)

            wp = WorkoutPlan.objects.create(
                user=request.user,
                experience=experience,
                goal=goal,
                metrics_json={"age": age, "rhr": rhr, "tenrm": tenrm_map},
                plan_json=plan,
            )
            messages.success(request, "Workout plan created.")
            return redirect("workout:plan_detail", pk=wp.pk)
    else:
        form = PreferenceForm()
    return render(request, "workout/new_plan.html", {"form": form})

@login_required
def plan_detail(request, pk: int):
    wp = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)
    plan = wp.plan_json or {}
    ctx = {
        "wp": wp,
        "meta": plan.get("meta") or {},
        "weeks": plan.get("weeks") or [],
        "zones": plan.get("zones") or [],
    }
    return render(request, "workout/plan_detail.html", ctx)

@login_required
def export_plan_csv(request, pk: int):
    wp = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)
    rows = plan_to_rows(wp.plan_json or {})
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = f'attachment; filename="workout_plan_{pk}.csv"'
    writer = csv.DictWriter(resp, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    return resp
