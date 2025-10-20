from django.urls import path
from .views import PostList


app_name = "blog"

urlpatterns = [
    path('', PostList.as_view(), name="home"),  
    path('posts/', PostList.as_view(), name="home"),
]

