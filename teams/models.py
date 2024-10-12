
# Create your models here.

from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100)
    sport = models.CharField(max_length=50)
    number_of_players = models.IntegerField()
    logo = models.ImageField(upload_to='team_logos/')

    def __str__(self):
        return self.name

class Player(models.Model):
    POSITION_CHOICES = [
        ('Forward', 'Forward'),
        ('Midfielder', 'Midfielder'),
        ('Defender', 'Defender'),
        ('Goalkeeper', 'Goalkeeper'),
    ]
    team = models.ForeignKey(Team, related_name='players', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='player_pictures/')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    date_of_birth = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    