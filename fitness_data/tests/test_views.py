from django.test import TestCase
from django.urls import reverse

class TestFitnessViews(TestCase):
    def test_fitness_page_get(self):
        url = reverse("fitness_data:fitness_page")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "BMI")   # tweak to a reliable string on the page
