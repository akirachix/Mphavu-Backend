
from rest_framework import serializers
from video_records.models import VideoRecord



class VideoRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoRecord
        fields = ['player_id', 'video_description', 'video_file', 'shooting_accuracy', 'shooting_angle']

    