from django import forms
from .models import ExperienceLevel, TrainingGoal

class PreferenceForm(forms.Form):
    experience = forms.ChoiceField(choices=ExperienceLevel.choices, label="Experience")
    goal = forms.ChoiceField(choices=TrainingGoal.choices, label="Goal")
    age = forms.IntegerField(required=False, widget=forms.HiddenInput)
    rhr = forms.IntegerField(required=False, widget=forms.HiddenInput)
    tenrm_json = forms.CharField(required=False, widget=forms.HiddenInput)
