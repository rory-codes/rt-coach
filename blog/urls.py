from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostList.as_view(), name="home"),
    path("<slug:slug>/", views.post_detail, name="post_detail"),
    path("<slug:slug>/comment/<int:comment_id>/edit/", views.comment_edit, name="comment_edit"),
]

