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
from django.views.decorators.csrf import csrf_exempt
from video_records.models import VideoRecord 
from .serializers import VideoRecordSerializer
import logging
from .serializers import PerformanceSerializer
from teams.models import Team, Player
from .serializers import TeamSerializer, PlayerSerializer
from django.http import HttpResponse
from video_analysis.forms import VideoUploadForm
from video_analysis.models import FootballVideo
from api.serializers import LoginSerializer, RegisterSerializer, PlayerSerializer
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
    
@csrf_exempt
def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
           
            uploaded_video_path = video.video_file.path
            compressed_video_path = compress_video(uploaded_video_path)
            if compressed_video_path:
                shooting_accuracy, shooting_angle = analyze_video(compressed_video_path)
                video.shooting_accuracy = shooting_accuracy
                video.shooting_angle = shooting_angle
                video.save()
                return HttpResponse(f"Shooting Accuracy: {shooting_accuracy:.2f}%, Shooting Angle: {shooting_angle:.2f}°")
    else:
        form = VideoUploadForm()
    return render(request, 'upload.html', {'form': form})

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
        

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            group_permissions = Permission.objects.filter(group__user=user).values_list('codename', flat=True)
            user_permissions = user.user_permissions.values_list('codename', flat=True)
            all_permissions = set(group_permissions) | set(user_permissions)
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
            user = authenticate(request, username=email, password=password)  # Adjust as needed

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



# Handles listing and creating players
class PlayerListView(APIView):
    def get(self, request):
        players = Player.objects.all()
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Handles retrieval, update, and deletion of a single player
class PlayerDetailView(APIView):
    def get(self, request, player_id):
        player = get_object_or_404(Player, pk=player_id)
        serializer = PlayerSerializer(player)
        return Response(serializer.data)

    def put(self, request, player_id):
        player = get_object_or_404(Player, pk=player_id)
        serializer = PlayerSerializer(player, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
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
    
