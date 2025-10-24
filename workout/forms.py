from django import forms
from .models import ExperienceLevel, TrainingGoal

class PreferenceForm(forms.Form):
    experience = forms.ChoiceField(
        choices=ExperienceLevel.choices, label="Experience level"
    )
    goal = forms.ChoiceField(
        choices=TrainingGoal.choices, label="Primary goal"
    )
    # Hidden fields for metrics when posting from fitness_data (optional, can be left blank)
    age = forms.IntegerField(required=False, widget=forms.HiddenInput)
    rhr = forms.IntegerField(required=False, widget=forms.HiddenInput)
    # A JSON string of 10RMs by exercise name (we'll parse in the view)
    tenrm_json = forms.CharField(required=False, widget=forms.HiddenInput)
