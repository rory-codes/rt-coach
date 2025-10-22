from django.contrib import admin
from .models import fitness_data
from django_summernote.admin import SummernoteModelAdmin


@admin.register(fitness_data)
class AboutAdmin(SummernoteModelAdmin):

    summernote_fields = ('content',)