
from rest_framework import serializers
from video_records.models import VideoRecord
from teams.models import Team, Player
from performance.models import Performance  
from django.contrib.auth import get_user_model
from users.models import User
# from players.models import Player
from emailsender.models import EmailInvite
from video_analysis.models import FootballVideo
from performance.models import Performance

class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = '__all__'


class VideoRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoRecord
        fields = ['player_id', 'video_description', 'video_file', 'shooting_accuracy', 'shooting_angle']
    
class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class PlayersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'registered_from', 'profile_picture', 'location']

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'role']
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data.get('role', User.COACH)  # Default role
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
 
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    
     
class NormalizedChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        # Normalize the input to lowercase
        data = data.lower()
        return super().to_internal_value(data)
    
class EmailInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailInvite
        fields = ['email']


class CoachSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields


class AgentSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields
class FootballVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootballVideo
        fields = '__all__'

    def validate_player_id(self, value):
        if not Player.objects.filter(id=value).exists():
            raise serializers.ValidationError("Player with that ID does not exist.")
        return value
