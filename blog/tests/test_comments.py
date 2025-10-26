from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from blog.models import Post, Comment

User = get_user_model()

class TestCommentPermissions(TestCase):
    def setUp(self):
        self.author = User.objects.create_user("author", password="p")
        self.other  = User.objects.create_user("other",  password="p")
        self.post = Post.objects.create(title="t", slug="t", author=self.author, content="x", status=1)
        self.comment = Comment.objects.create(post=self.post, author=self.author, body="hi", approved=True)

    def test_only_owner_can_edit(self):
        url = reverse("blog:comment_edit", args=[self.post.slug, self.comment.id])
        self.client.login(username="other", password="p")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (403, 302))  # your view either forbids or redirects
