from django.test import TestCase
from .models import Performance
class PerformanceModelTest(TestCase):
    def setUp(self):
        """Create a Performance instance for testing."""
        self.performance = Performance.objects.create(
            player_id=1,  # Assuming this player ID exists in your database
            passes=5,
            assists=2,
            no_of_goals=1,
            shots_on_target=3
        )
    def test_performance_str(self):
        """Test the string representation of the Performance model."""
        self.assertEqual(str(self.performance), "Performance 1 for Player 1")
    def test_performance_creation(self):
        """Test the creation of a Performance instance."""
        self.assertEqual(self.performance.player_id, 1)
        self.assertEqual(self.performance.passes, 5)
        self.assertEqual(self.performance.assists, 2)
        self.assertEqual(self.performance.no_of_goals, 1)
        self.assertEqual(self.performance.shots_on_target, 3)
    def test_performance_fields(self):
        """Test the data types of the Performance model fields."""
        self.assertIsInstance(self.performance.passes, int)
        self.assertIsInstance(self.performance.assists, int)
        self.assertIsInstance(self.performance.no_of_goals, int)
        self.assertIsInstance(self.performance.shots_on_target, int)
        self.assertIsInstance(self.performance.player_id, int)




