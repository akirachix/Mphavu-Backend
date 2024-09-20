from rest_framework import serializers
from teams.models import Team, Player
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'profile_picture', 'position', 'date_of_birth', 'team']
class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    class Meta:
        model = Team
        fields = ['id', 'name', 'sport', 'number_of_players', 'logo', 'players']