from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include(("blog.urls", "blog"), namespace="blog")),
    path("fitness_data/", include("fitness_data.urls"), name="fitness_data-urls"),
    path('summernote/', include('django_summernote.urls')),
]
