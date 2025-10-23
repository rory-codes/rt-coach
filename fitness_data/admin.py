from django.contrib import admin
from .models import FitnessData
from django_summernote.admin import SummernoteModelAdmin


@admin.register(FitnessData)
class AboutAdmin(SummernoteModelAdmin):

    summernote_fields = ('content',)