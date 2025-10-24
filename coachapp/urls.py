# coachapp/urls.py (project-level)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("fitness/", include("fitness_data.urls")),
    path("summernote/", include("django_summernote.urls")),
    path("workout/", include(("workout.urls", "workout"), namespace="workout")),
    path("", include(("blog.urls", "blog"), namespace="blog")),
]