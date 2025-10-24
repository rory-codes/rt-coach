from django.conf import settings
from django.db import models
from django.utils import timezone

class ExperienceLevel(models.TextChoices):
    BEGINNER = "beginner", "Beginner"
    INTERMEDIATE = "intermediate", "Intermediate"
    EXPERIENCED = "experienced", "Experienced"

class TrainingGoal(models.TextChoices):
    CARDIO = "cardio", "Improve cardio fitness"
    STRENGTH = "strength", "Improve strength"
    BALANCED = "balanced", "Improve health (balanced)"

class WorkoutPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="workout_plans")
    experience = models.CharField(max_length=20, choices=ExperienceLevel.choices)
    goal = models.CharField(max_length=20, choices=TrainingGoal.choices)
    metrics_json = models.JSONField(default=dict, blank=True)
    plan_json = models.JSONField(default=dict, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
