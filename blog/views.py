# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Post, Comment
from .forms import CommentForm


class PostList(ListView):
    queryset = Post.objects.filter(status=1)
    template_name = "blog/index.html"
    paginate_by = 6
    context_object_name = "post_list"


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.filter(status=1), slug=slug)
    comments = post.comments.all().order_by("-created_on")
    comment_count = post.comments.filter(approved=True).count()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to comment.")
            return redirect("account_login")

        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            # comment.approved = False  # if moderation required
            comment.save()
            messages.success(request, "Comment submitted and awaiting approval")
            return redirect(request.path + "#comments")
    else:
        form = CommentForm()

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_count": comment_count,
            "comment_form": form,
        },
    )


@login_required
def comment_edit(request, slug, comment_id):
    """
    Show an edit form on GET; update on POST.
    Only the original author may edit.
    """
    post = get_object_or_404(Post, slug=slug, status=1)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)

    if comment.author != request.user:
        messages.error(request, "You can only edit your own comments.")
        return redirect("blog:post_detail", slug=slug)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            edited = form.save(commit=False)
            edited.post = post
            edited.approved = False  # re-moderate if you want
            edited.save()
            messages.success(request, "Comment updated!")
            return redirect("blog:post_detail", slug=slug)
        else:
            messages.error(request, "Error updating comment.")
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "blog/comment_edit.html",
        {"post": post, "form": form, "comment": comment},
    )
