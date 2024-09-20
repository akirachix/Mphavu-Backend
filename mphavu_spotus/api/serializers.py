
from rest_framework import serializers
from video_records.models import VideoRecord
from teams.models import Team, Player
from performance.models import Performance  

class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = '__all__'
class VideoRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoRecord
        fields = ['player_id', 'video_description', 'video_file', 'shooting_accuracy', 'shooting_angle']
    
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'profile_picture', 'position', 'date_of_birth', 'team']
class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    class Meta:
        model = Team
        fields = ['id', 'name', 'sport', 'number_of_players', 'logo', 'players']
