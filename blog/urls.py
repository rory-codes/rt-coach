from django.urls import path
from .views import PostList
from . import views


app_name = "blog"

urlpatterns = [
    path('', PostList.as_view(), name="home"),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]

