from django.urls import path 
from .views import PerformanceListView, VideoRecordListView, VideoRecordDetailView
from .views import  PerformanceDetailView, TeamDetailView, TeamPlayersListView,TeamPlayersDetailView, PlayersDetailView, PlayersListView
from django.urls import path
from .views import (
    LoginUser,
    RegisterView,
    UserListView,
)
from django.conf import settings
from django.conf.urls.static import static
from .views import InviteView, TeamListView
from .views import (
    upload_video,
    FootballVideoListView,
    FootballVideoDetailView,
    PlayerFootballVideoListView,
    PlayerFootballVideoDetailView
)
from .import views


urlpatterns = [
    path('performance/', PerformanceListView.as_view(), name='performance-list'),
    path('players/<int:player_id>/performances/', PerformanceDetailView.as_view(), name='player-performance-list'),
   path('video_records/', VideoRecordListView.as_view(), name='video_record_list'),
   path('video_records/<int:video_record_id>/', VideoRecordDetailView.as_view(), name='video_record_detail'),
   path('players/<int:player_id>/performances/', PerformanceDetailView.as_view(), name='player-performance-list'),
   path('register/', RegisterView.as_view(), name='register'),  # Endpoint for user registration
   path('users/', UserListView.as_view(), name='all_users'),   # Endpoint to list all users
   path('user/login/', LoginUser.as_view(), name='login'), 
   path('send-invite/', InviteView.as_view(), name='send-invite'),
   path('teams/', TeamListView.as_view(), name='team_list'),
   path('teams/<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
   path('player/', PlayersListView.as_view(), name='player_list'),
   path('player/<int:pk>/', PlayersDetailView.as_view(), name='player_detail'),
   path('teams/<int:team_id>/players/', TeamPlayersListView.as_view(), name='team_players_list'),
   path('teams/<int:team_id>/players/<int:player_id>/', TeamPlayersDetailView.as_view(), name='team_player_detail'),
   path('player/upload/', upload_video, name='upload_video'),
   path('videos/', FootballVideoListView.as_view(), name='football_video_list'),
   path('videos/<int:video_id>/', FootballVideoDetailView.as_view(), name='video-detail'),
   path('player/<int:player_id>/videos/', PlayerFootballVideoListView.as_view(), name='player-video-list'),
   path('player/<int:player_id>/videos/<int:video_id>/', PlayerFootballVideoDetailView.as_view(), name='player-video-detail'),
   path('coaches/', views.coaches_view, name='coaches_view'), 
   path('agents/', views.agents_view, name='agents_view'),
  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
