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
    """Stores a generated plan (snapshot) so user can revisit it."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="workout_plans"
    )
    experience = models.CharField(max_length=20, choices=ExperienceLevel.choices)
    goal = models.CharField(max_length=20, choices=TrainingGoal.choices)
    # Raw inputs used to compute the plan (age, rhr, 10rms, weight, etc.)
    metrics_json = models.JSONField(default=dict, blank=True)
    # The rendered, structured plan
    plan_json = models.JSONField(default=dict, blank=True)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.get_experience_display()} · {self.get_goal_display()} · {self.created_on:%Y-%m-%d}"
