from django.db import models
from django.conf import settings 

class Team(models.Model):
    name = models.CharField(max_length=100)
    coach = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Player(models.Model):
    POSITION_CHOICES = [
        ('Goalkeeper', 'Goalkeeper'),
        ('Defender', 'Defender'),
        ('Striker', 'Striker'),
    ]
    
    TEAM_CHOICES = [
        ('Kipaji', 'Kipaji'),
        ('Ligi Ndogo', 'Ligi Ndogo'),
        ('NextGen', 'NextGen'),
    ]

    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    position = models.CharField(max_length=30, choices=POSITION_CHOICES)

    def __str__(self):
        return self.name
