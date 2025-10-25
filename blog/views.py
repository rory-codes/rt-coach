# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST   # ← add this
from django.urls import reverse
from .models import Post, Comment                       # ← remove ", delete"
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
            # comment.approved = False  # enable if you want moderation on new comments
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
    post = get_object_or_404(Post, slug=slug, status=1)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)

    if comment.author != request.user and not request.user.is_staff:
        messages.error(request, "You can only edit your own comments.")
        return redirect("blog:post_detail", slug=slug)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            edited = form.save(commit=False)
            edited.post = post
            edited.approved = False   # re-moderate after edits (optional)
            edited.save()
            messages.success(request, "Comment updated!")
            return redirect("blog:post_detail", slug=slug)
        messages.error(request, "Error updating comment.")
    else:
        form = CommentForm(instance=comment)

    return render(request, "blog/comment_edit.html", {"post": post, "form": form, "comment": comment})


@require_POST
@login_required
def comment_delete(request, slug, comment_id):
    post = get_object_or_404(Post.objects.filter(status=1), slug=slug)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)

    if request.user == comment.author or request.user.is_staff:
        comment.delete()
        messages.success(request, "Comment deleted.")
    else:
        messages.error(request, "You do not have permission to delete this comment.")

    return redirect(reverse("blog:post_detail", args=[slug]) + "#comments")
