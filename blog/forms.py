# blog/forms.py
from django import forms
from .models import Comment  # requires Comment model in blog/models.py

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4, "placeholder": "Write your comment…"}),
        }
