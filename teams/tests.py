from django.test import TestCase
from .models import Team, Player
class TeamModelTest(TestCase):
    def setUp(self):
        """Create a team instance for testing."""
        self.team = Team.objects.create(
            name="Golden Eagles",
            sport="Soccer",
            number_of_players=11,
            logo="path/to/logo.jpg"  # Mocked path for testing
        )
    def test_team_str(self):
        """Test the string representation of the Team model."""
        self.assertEqual(str(self.team), "Golden Eagles")
    def test_team_creation(self):
        """Test the creation of a Team instance."""
        self.assertEqual(self.team.name, "Golden Eagles")
        self.assertEqual(self.team.sport, "Soccer")
        self.assertEqual(self.team.number_of_players, 11)
class PlayerModelTest(TestCase):
    def setUp(self):
        """Create a team instance and player instance for testing."""
        self.team = Team.objects.create(
            name="Golden Eagles",
            sport="Soccer",
            number_of_players=11,
            logo="path/to/logo.jpg"  # Mocked path for testing
        )
        self.player = Player.objects.create(
            team=self.team,
            first_name="John",
            last_name="Doe",
            profile_picture="path/to/profile.jpg",  # Mocked path for testing
            position="Forward",
            date_of_birth="2000-01-01"
        )
    def test_player_str(self):
        """Test the string representation of the Player model."""
        self.assertEqual(str(self.player), "John Doe")
    def test_player_creation(self):
        """Test the creation of a Player instance."""
        self.assertEqual(self.player.first_name, "John")
        self.assertEqual(self.player.last_name, "Doe")
        self.assertEqual(self.player.position, "Forward")
        self.assertEqual(self.player.date_of_birth, "2000-01-01")
        self.assertEqual(self.player.team, self.team)











