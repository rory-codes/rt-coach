from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView
from .models import Post, Comment


# Create your views here.
class PostList(ListView):
    model = Post
    template_name = "blog/post_list.html" 