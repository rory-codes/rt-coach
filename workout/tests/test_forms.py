from django.test import SimpleTestCase
from workout.forms import WorkoutPlanForm  # or NewPlanForm if you created it

class TestWorkoutPlanForm(SimpleTestCase):
    def test_minimum_valid(self):
        form = WorkoutPlanForm(data={
            "experience": "beginner",
            "goal": "balanced",
            # include hidden fields if required by the form:
            "age": 30,
            "rhr": 55,
            "tenrm_json": "{}",
        })
        self.assertTrue(form.is_valid(), form.errors.as_json())
