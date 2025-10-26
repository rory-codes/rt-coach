from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class TestWorkoutViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p")

    def test_new_plan_requires_login(self):
        url = reverse("workout:new")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (302, 301))  # redirected to login

    def test_new_plan_post_creates_plan(self):
        self.client.login(username="u", password="p")
        url = reverse("workout:new")
        resp = self.client.post(url, {
            "experience": "beginner",
            "goal": "balanced",
            "age": 30,
            "rhr": 55,
            "tenrm_json": "{}",
        })
        self.assertIn(resp.status_code, (302, 303))  # PRG redirect to detail
