
from rest_framework import serializers
from video_records.models import VideoRecord
from teams.models import Team, Player
from performance.models import Performance  
from django.contrib.auth import get_user_model
from users.models import User
from players.models import Player
from emailsender.models import EmailInvite
from video_analysis.models import FootballVideo


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
User = get_user_model()
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
 
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'      
class NormalizedChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        # Normalize the input to lowercase
        data = data.lower()
        return super().to_internal_value(data)
    
class EmailInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailInvite
        fields = ['email']

class FootballVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootballVideo
        fields = ['id', 'video_file', 'player_name', 'shooting_accuracy', 'shooting_angle', 'player_id']   
