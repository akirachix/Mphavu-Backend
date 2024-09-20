from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework import status 
import os
from django.shortcuts import get_object_or_404
from django.conf import settings
import subprocess
from video_records.models import VideoRecord 
from .serializers import VideoRecordSerializer
import logging
from .serializers import PerformanceSerializer
from teams.models import Team, Player
from .serializers import TeamSerializer, PlayerSerializer

logger = logging.getLogger(__name__)
"""
Handle GET requests to retrieve a list of video records.
Retrieve all VideoRecord instances from the database.
"""
class VideoRecordListView(APIView):
    def get(self, request):
        video_records = VideoRecord.objects.all()
        serializer = VideoRecordSerializer(video_records, many=True)
        return Response(serializer.data)
    
    """
    command to compress the video
    will invoke the ffmpeg program to run
    Input video
    Video codec
    controls the quality of the ouput
    Encoding speed
    Output video
    """

    def post(self, request):
        serializer = VideoRecordSerializer(data=request.data)
        if serializer.is_valid():
            video_record = serializer.save()  
            
            input_file_path = video_record.video_file.path
            file_extension = os.path.splitext(input_file_path)[1].lower()

            if file_extension in ['.webm', '.avi', '.mov']:
                output_file_path = os.path.join(settings.MEDIA_ROOT, 'compressed_videos', f'{os.path.splitext(os.path.basename(input_file_path))[0]}.mp4')
            else:
                output_file_path = os.path.join(settings.MEDIA_ROOT, 'compressed_videos', os.path.basename(input_file_path))
            
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            
            ffmpeg_command = [
                'ffmpeg', 
                '-i', input_file_path, 
                '-vcodec', 'libx264',  
                '-crf', '28',  
                '-preset', 'fast',  
                '-an',  
                output_file_path  
            ]
            
            ffmpeg_process = subprocess.run(ffmpeg_command, capture_output=True, text=True)

            if ffmpeg_process.returncode == 0:
                logger.info(ffmpeg_process.stdout)
                video_record.video_file.name = f'compressed_videos/{os.path.basename(output_file_path)}'
                video_record.save()  
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"FFmpeg error: {ffmpeg_process.stderr}")
                return Response({"detail": f"FFmpeg error: {ffmpeg_process.stderr}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""
Retrieve the VideoRecord instance.
Serialize the video record.
Retrieve the VideoRecord instance.
"""    
class VideoRecordDetailView(APIView):
    def get(self, request, video_record_id):
        if VideoRecord.objects.filter(pk=video_record_id).exists():
            video_record = VideoRecord.objects.get(pk=video_record_id)
            serializer = VideoRecordSerializer(video_record)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, video_record_id):
        if VideoRecord.objects.filter(pk=video_record_id).exists():
            video_record = VideoRecord.objects.get(pk=video_record_id)
            serializer = VideoRecordSerializer(video_record, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, video_record_id):
        if VideoRecord.objects.filter(pk=video_record_id).exists():
            video_record = VideoRecord.objects.get(pk=video_record_id)
            video_record.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class TeamListCreate(APIView):
    def get(self, request):
        queryset = Team.objects.all()
        name = request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        serializer = TeamSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Team added successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeamDetail(APIView):
    def get(self, request, pk):
        team = Team.objects.filter(pk=pk)
        if team.exists():
            serializer = TeamSerializer(team.first())
            return Response(serializer.data)
        return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)

class PlayerListCreate(APIView):
    def get(self, request, team_id):
        queryset = Player.objects.filter(team_id=team_id)
        serializer = PlayerSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, team_id):
        data = request.data.copy()
        data['team'] = team_id
        serializer = PlayerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Player added successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PlayerDetail(APIView):
    def get(self, request, pk):
        player = Player.objects.filter(pk=pk)
        if player.exists():
            serializer = PlayerSerializer(player.first())
            return Response(serializer.data)
        return Response({'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)


class PerformanceListView(APIView):
    def get(self, request):
        # Get all performances
        performances = Performance.objects.all()
        serializer = PerformanceSerializer(performances, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PerformanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PerformanceDetailView(APIView):
    def get(self, request, player_id):
        try:
            # Get performances for the specified player
            performances = Performance.objects.get(player_id=player_id)
            serializer = PerformanceSerializer(performances)
            return Response(serializer.data)
        except Performance.DoesNotExist:
            return Response({"detail": "No performances found for this player."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, player_id):
        try:
            # Get the performance for the specific player
            performance = Performance.objects.get(player_id=player_id)
            serializer = PerformanceSerializer(performance, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Performance.DoesNotExist:
            return Response({"detail": "Performance not found for this player."}, status=status.HTTP_404_NOT_FOUND)