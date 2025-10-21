from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView
from .models import Post, Comment


# Create your views here.
class PostList(ListView):
    queryset = Post.objects.filter(status=1)
    template_name = "blog/index.html"
    paginate_by = 6