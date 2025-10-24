# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import CommentForm

class PostList(ListView):
    queryset = Post.objects.filter(status=1)
    template_name = "blog/index.html"
    paginate_by = 6
    context_object_name = "post_list"

def post_detail(request, slug):
    """
    Display an individual :model:`blog.Post`.
    """
    post = get_object_or_404(Post.objects.filter(status=1), slug=slug)

    # comments
    comments = post.comments.all().order_by("-created_on")
    comment_count = post.comments.filter(approved=True).count()

    if request.method == "POST":
        print("Received a POST request")
        # must be logged in to post
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to comment.")
            return redirect("account_login")

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            # Optional: hold for moderation
            # comment.approved = False
            comment.save()

            messages.success(request, "Comment submitted and awaiting approval")
            # PRG pattern: redirect to avoid resubmission on refresh
            return redirect(request.path + "#comments")
    else:
        comment_form = CommentForm()
        print("About to render template")

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_count": comment_count,
            "comment_form": comment_form,
        },
    )
