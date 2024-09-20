from django.test import TestCase

# Create your tests here.



from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from teams.models import Team, Player
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

class TeamTests(APITestCase):
    def create_image(self, name):
        image = Image.new('RGB', (100, 100), color='blue')
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return SimpleUploadedFile(name=name, content=img_byte_arr.getvalue(), content_type='image/png')

    def test_create_team(self):
        url = reverse('team-list-create')
        logo = self.create_image('logo.png')

        data = {
            'name': 'Test Team',
            'sport': 'Soccer',
            'number_of_players': 11,
            'logo': logo,
        }

        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Team added successfully')

    def test_get_all_teams(self):
        Team.objects.create(name='Team 1', sport='Soccer', number_of_players=11, logo=self.create_image('logo1.png'))
        Team.objects.create(name='Team 2', sport='Basketball', number_of_players=5, logo=self.create_image('logo2.png'))

        url = reverse('team-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_teams_by_name(self):
        Team.objects.create(name='Team Awesome', sport='Soccer', number_of_players=11, logo=self.create_image('logo.png'))
        Team.objects.create(name='Team Average', sport='Soccer', number_of_players=11, logo=self.create_image('logo.png'))

        url = reverse('team-list-create') + '?name=Awesome'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_team_detail(self):
        team = Team.objects.create(name='Team Detail', sport='Soccer', number_of_players=11, logo=self.create_image('logo.png'))
        url = reverse('team-detail', kwargs={'pk': team.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], team.name)

    def test_get_non_existent_team(self):
        url = reverse('team-detail', kwargs={'pk': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Team not found')


class PlayerTests(APITestCase):
    def create_image(self, name):
        image = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return SimpleUploadedFile(name=name, content=img_byte_arr.getvalue(), content_type='image/png')

    def setUp(self):
        self.team = Team.objects.create(
            name='Test Team',
            sport='Soccer',
            number_of_players=11,
            logo=self.create_image('logo.png'),
        )

    def test_create_player(self):
        url = reverse('player-list-create', kwargs={'team_id': self.team.id})
        profile_picture = self.create_image('profile_picture.png')

        data = {
            'first_name': 'Test',
            'last_name': 'Player',
            'profile_picture': profile_picture,
            'position': 'Forward',
            'date_of_birth': '2000-01-01',
            'team': self.team.id,
        }

        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Player added successfully')

    def test_get_all_players(self):
        Player.objects.create(first_name='Player 1', last_name='Test', profile_picture=self.create_image('player1.png'), position='Forward', date_of_birth='2000-01-01', team=self.team)
        Player.objects.create(first_name='Player 2', last_name='Test', profile_picture=self.create_image('player2.png'), position='Midfielder', date_of_birth='2000-01-01', team=self.team)

        url = reverse('player-list-create', kwargs={'team_id': self.team.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_player_detail(self):
        player = Player.objects.create(first_name='Player Detail', last_name='Test', profile_picture=self.create_image('profile.png'), position='Defender', date_of_birth='2000-01-01', team=self.team)
        url = reverse('player-detail', kwargs={'pk': player.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], player.first_name)

    def test_get_non_existent_player(self):
        url = reverse('player-detail', kwargs={'pk': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Player not found')
