from django.contrib import admin
from .models import WorkoutPlan

@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "experience", "goal", "created_on")
    list_filter = ("experience", "goal", "created_on")
    search_fields = ("user__username",)