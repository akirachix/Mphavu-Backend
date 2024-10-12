from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Team, Player

User = get_user_model()

class TeamModelTest(TestCase):

    def setUp(self):
        # Create a user for the coach without a username
        self.coach = User.objects.create_user(
            email='coach1@example.com',  # Using email as identifier
            password='testpass123'
        )

    def test_team_creation(self):
        team = Team.objects.create(name='Kipaji', coach=self.coach)
        self.assertEqual(str(team), 'Kipaji')
        self.assertEqual(team.coach.email, 'coach1@example.com')

class PlayerModelTest(TestCase):

    def setUp(self):
        # Create a user for the coach without a username
        self.coach = User.objects.create_user(
            email='coach2@example.com',  # Using email as identifier
            password='testpass123'
        )
        self.team = Team.objects.create(name='Ligi Ndogo', coach=self.coach)

    def test_player_creation(self):
        player = Player.objects.create(
            name='John Doe',
            date_of_birth='2000-01-01',
            position='Striker'
        )
        self.assertEqual(str(player), 'John Doe')
        self.assertEqual(player.position, 'Striker')

    def test_player_team_relationship(self):
        player = Player.objects.create(
            name='Jane Doe',
            date_of_birth='1995-05-05',
            position='Defender'
        )
        # Assuming you add a team field to Player model
        player.team = self.team  
        player.save()

        self.assertEqual(player.team.name, 'Ligi Ndogo')
        self.assertEqual(player.team.coach.email, 'coach2@example.com')
