from django.shortcuts import render
from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework import status 
import os
from django.shortcuts import get_object_or_404
from django.conf import settings
import subprocess
import cv2
import numpy as np
from .serializers import FootballVideoSerializer
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from performance.models import Performance
from video_records.models import VideoRecord 
from .serializers import VideoRecordSerializer
import logging
from .serializers import PerformanceSerializer
from teams.models import Team, Player
from .serializers import TeamSerializer
from django.http import HttpResponse, JsonResponse
from video_analysis.forms import VideoUploadForm
from video_analysis.models import FootballVideo
from api.serializers import LoginSerializer, RegisterSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Permission
from emailsender.models import EmailInvite
from emailsender.utils import send_invite
from .serializers import EmailInviteSerializer
from django.core.mail import send_mail

from teams.models import Team, Player
from .serializers import TeamSerializer, PlayersSerializer, UserSerializer

# Team Views
class TeamListView(APIView):
    """
    Handles listing all teams and creating a new team.
    """
    def get(self, request):
        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamDetailView(APIView):
    """
    Handles retrieving, updating, and deleting a specific team by ID.
    """
    def get(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        serializer = TeamSerializer(team)
        return Response(serializer.data)

    def put(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        serializer = TeamSerializer(team, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TeamDetailWithPlayersView(APIView):
    """
    Handles retrieving a specific team by ID along with its players.
    """
    def get(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        serializer = TeamSerializer(team)
        players = team.players.all()
        players_serializer = PlayersSerializer(players, many=True)
        return Response({
            'team': serializer.data,
            'players': players_serializer.data
        })
# Player Views
class PlayersListView(APIView):
    """
    Handles listing all players and creating a new player.
    """
    def get(self, request):
        players = Player.objects.all()
        serializer = PlayersSerializer(players, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PlayersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayersDetailView(APIView):
    """
    Handles retrieving, updating, and deleting a specific player by ID.
    """
    def get(self, request, pk):
        player = get_object_or_404(Player, pk=pk)
        serializer = PlayersSerializer(player)
        return Response(serializer.data)

    def put(self, request, pk):
        player = get_object_or_404(Player, pk=pk)
        serializer = PlayersSerializer(player, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        player = get_object_or_404(Player, pk=pk)
        player.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamPlayersListView(APIView):
    """
    Handles listing all players of a specific team and creating a new player for the team.
    """
    def get(self, request, team_id):
        team = get_object_or_404(Team, pk=team_id)
        players = team.players.all()
        serializer = PlayersSerializer(players, many=True)
        return Response(serializer.data)

    def post(self, request, team_id):
        team = get_object_or_404(Team, pk=team_id)
        data = request.data.copy()
        data['team'] = team.id  # Associate the player with the team
        serializer = PlayersSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamPlayersDetailView(APIView):
    """
    Handles retrieving, updating, and deleting a specific player of a specific team.
    """
    def get(self, request, team_id, player_id):
        # Get the team or return 404
        team = get_object_or_404(Team, pk=team_id)

        # Get the player who belongs to the specific team or return 404
        player = get_object_or_404(Player, pk=player_id, team=team)

        # Serialize and return the player data
        serializer = PlayersSerializer(player)
        return Response(serializer.data)

    def put(self, request, team_id, player_id):
        team = get_object_or_404(Team, pk=team_id)
        player = get_object_or_404(Player, pk=player_id, team=team)

        data = request.data.copy()
        data['team'] = team.id  # Ensure the player remains associated with the team
        serializer = PlayersSerializer(player, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, team_id, player_id):
        team = get_object_or_404(Team, pk=team_id)
        player = get_object_or_404(Player, pk=player_id, team=team)
        player.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Upload and Analyze Video
# Upload and Analyze Video
@api_view(['POST'])
def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded video
            video = form.save()
            uploaded_video_path = video.video_file.path
            
            # Compress the video
            compressed_video_path = compress_video(uploaded_video_path)
            if compressed_video_path:
                # Analyze the video and get shooting accuracy (in percentage) and shooting angle (in degrees)
                shooting_accuracy, shooting_angle = analyze_video(compressed_video_path)
                
                # Update the video instance with the analyzed values
                video.shooting_accuracy = shooting_accuracy
                video.shooting_angle = shooting_angle
                video.save()

                # Use the serializer to include all fields in the response
                serializer = FootballVideoSerializer(video)

                return Response({
                    'message': 'Video uploaded and processed successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)

        return Response({'error': 'Invalid form data'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

# Helper function to compress video
def compress_video(video_path):
    compressed_video_path = os.path.splitext(video_path)[0] + '_compressed.mp4'
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vcodec', 'libx264',    
        '-crf', '28',            
        '-preset', 'medium',      
        '-y',                     
        compressed_video_path
    ]
    
    try:
        subprocess.run(command, check=True)
        return compressed_video_path
    except subprocess.CalledProcessError as e:
        print(f"Error during compression: {e}")
        return None

# Helper function to analyze video
def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)

    total_frames = 0
    successful_shots = 0
    angle_sum = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        total_frames += 1

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_color = np.array([20, 100, 100]) 
        upper_color = np.array([30, 255, 255])
        
        mask = cv2.inRange(hsv_frame, lower_color, upper_color)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 500:  
                successful_shots += 1

                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    
                    center_x = frame.shape[1] // 2
                    center_y = frame.shape[0] // 2
                    angle = np.arctan2(cY - center_y, cX - center_x) * (180 / np.pi)
                    angle_sum += abs(angle)

    cap.release()

    shooting_accuracy = (successful_shots / total_frames) * 100 if total_frames > 0 else 0
    shooting_angle = angle_sum / successful_shots if successful_shots > 0 else 0

    return shooting_accuracy, shooting_angle

# List all analyzed videos
class FootballVideoListView(APIView):
    def get(self, request):
        videos = FootballVideo.objects.all()
        serializer = FootballVideoSerializer(videos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Assuming you have a form or serializer for the video upload
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()

            uploaded_video_path = video.video_file.path
            
            # Compress the video
            compressed_video_path = compress_video(uploaded_video_path)
            if compressed_video_path:
                # Analyze the video and get shooting accuracy (in percentage) and shooting angle (in degrees)
                shooting_accuracy, shooting_angle = analyze_video(compressed_video_path)
                
                # Update the video instance with the analyzed values
                video.shooting_accuracy = shooting_accuracy  # Ensure this is in percentage
                video.shooting_angle = shooting_angle  # Ensure this is in degrees
                video.save()

                # Use the serializer to include all fields in the response
                serializer = FootballVideoSerializer(video)

                return Response({
                    'message': 'Video uploaded and processed successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)

        return Response({'error': 'Invalid form data'}, status=status.HTTP_400_BAD_REQUEST)

# Retrieve specific analyzed video by video ID
class FootballVideoDetailView(APIView):
    def get(self, request, video_id):
        video = get_object_or_404(FootballVideo, id=video_id)
        serializer = FootballVideoSerializer(video)
        return Response(serializer.data, status=status.HTTP_200_OK)

# List all analyzed videos for a specific player
class PlayerFootballVideoListView(APIView):
    def get(self, request, player_id):
        videos = FootballVideo.objects.filter(player_id=player_id)  # Filter videos by player_id
        serializer = FootballVideoSerializer(videos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, player_id):
        # Here you can handle video upload for a specific player
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)  # Don't save yet
            video.player_id = player_id  # Set the player_id
            video.save()  # Now save the instance

            # Process the video as before (compress, analyze, etc.)
            uploaded_video_path = video.video_file.path
            compressed_video_path = compress_video(uploaded_video_path)
            if compressed_video_path:
                shooting_accuracy, shooting_angle = analyze_video(compressed_video_path)
                video.shooting_accuracy = shooting_accuracy
                video.shooting_angle = shooting_angle
                video.save()

                serializer = FootballVideoSerializer(video)
                return Response({
                    'message': 'Video uploaded and processed successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)

        return Response({'error': 'Invalid form data'}, status=status.HTTP_400_BAD_REQUEST)


# Retrieve a specific analyzed video of a player
class PlayerFootballVideoDetailView(APIView):
    def get(self, request, player_id, video_id):
        try:
            # Query the video by both player_id and video_id
            video = FootballVideo.objects.get(player_id=player_id, id=video_id)
            serializer = FootballVideoSerializer(video)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FootballVideo.DoesNotExist:
            return Response({'error': 'Video not found for this player'}, status=status.HTTP_404_NOT_FOUND)


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

       



class PerformanceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        performances = Performance.objects.all()  # Get all performances
        serializer = PerformanceSerializer(performances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = PerformanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PerformanceDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, player_id, *args, **kwargs):
        performances = Performance.objects.filter(player_id=player_id)  # Get performances for specific player
        serializer = PerformanceSerializer(performances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, player_id, *args, **kwargs):
        data = request.data.copy()
        data['player_id'] = player_id  # Assign the player_id to the data
        serializer = PerformanceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        registered_via = 'admin'
        if get_user_model().objects.filter(email=email).exists():
            return Response({'error': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(registered_from=registered_via)
            response_data = {
                'message': f"{user.role.capitalize()} {user.first_name} {user.last_name} successfully created",
                'user': {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'role': user.role,
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UserDataMixin:
    def get_user_data(self, user):
        group_permissions = Permission.objects.filter(group__user=user).values_list('codename', flat=True)
        user_permissions = user.user_permissions.values_list('codename', flat=True)
        all_permissions = set(group_permissions)
        all_permissions.update(user_permissions)
        return {
            'user_id': user.user_id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role,
        }
class UserListView(UserDataMixin, APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        User = get_user_model()  # Use this to get the custom user model
        users = User.objects.all()
        user_data_list = [self.get_user_data(user) for user in users]
        return Response(user_data_list)
class LoginUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, username=email, password=password)  # Ensure this matches your USERNAME_FIELD
            if user:
                auth_login(request, user)
                response_data = {
                    'message': 'Login successful',
                    'user': {
                        'user_id': user.user_id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'role': user.role,
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InviteView(APIView):
    def post(self, request):
        serializer = EmailInviteSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                email_invite = serializer.save()
                
                send_invite(email)

                return Response({"message": "Invitation sent!"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_invite(email):
    send_mail(
        'Invitation to Join SpotUs',
        'Congratulations! You are invited to join SpotUs. Use this link to register. https://informational-website-sage.vercel.app/',
        'mphavuspotus@gmail.com',
        [email],
        fail_silently=False,
    )
@csrf_exempt   
@api_view(['GET', 'POST'])
def coaches_view(request):
    User = get_user_model()
    if request.method == 'GET':
        coaches = User.objects.filter(role=User.COACH, registered_from='coach')
        serializer = UserSerializer(coaches, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()
        data['role'] = User.COACH
        data['registered_from'] = 'coach'
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@csrf_exempt
@api_view(['GET', 'POST'])
def agents_view(request):
    User = get_user_model()
    if request.method == 'GET':
        agents = User.objects.filter(role=User.AGENT, registered_from='agent')
        serializer = UserSerializer(agents, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()
        data['role'] = User.AGENT
        data['registered_from'] = 'agent'
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET', 'POST'])
# def coaches_view(request):
#     User = get_user_model()
#     if request.method == 'GET':
#         # Filter to get only coaches registered specifically through this endpoint
#         coaches = User.objects.filter(role=User.COACH, registered_from='coach')
#         serializer = UserSerializer(coaches, many=True)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         data = request.data.copy()
#         data['role'] = User.COACH
#         data['registered_from'] = 'coach'  # Set the registration source
#         if User.objects.filter(email=data['email']).exists():
#             return Response({'error': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
#         serializer = UserSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# @api_view(['GET', 'POST'])
# def agents_view(request):
#     User = get_user_model()
#     if request.method == 'GET':
#         # Filter to get only agents registered specifically through this endpoint
#         agents = User.objects.filter(role=User.AGENT, registered_from='agent')
#         serializer = UserSerializer(agents, many=True)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         data = request.data.copy()
#         data['role'] = User.AGENT
#         data['registered_from'] = 'agent'  # Set the registration source
#         serializer = UserSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
def admin_dashboard_view(request):
    User = get_user_model()
    # Fetch all users
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
