from django.shortcuts import render
from .models import fitness_data


def about_me(request):
    """
    Renders the About page
    """
    fitness_data = fitness_data.objects.all().order_by('-updated_on').first()

    return render(
        request,
        "fitness_data/fitness_data.html",
        {"fitness_data": fitness_data},
    )