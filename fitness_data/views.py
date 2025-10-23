from django.shortcuts import render, get_object_or_404
from .models import FitnessData

def about_me(request):
    record = (FitnessData.objects
              .order_by("-updated_on")
              .first())
    return render(
        request,
        "fitness_data/fitness_data.html",
        {"fitness_data": record},
    )