from django.urls import path 
from .views import VideoRecordListView, VideoRecordDetailView
from .views import TeamListCreate, TeamDetail, PlayerListCreate, PlayerDetail
from .views import upload_video
from .views import PerformanceListView, PerformanceDetailView
from django.urls import path
from .views import (
    LoginUser,
    RegisterView,
    UserListView,
)
from django.conf import settings
from django.conf.urls.static import static
from .views import PlayerListView, PlayerDetailView
from .views import InviteView



urlpatterns = [
   path('video_records/', VideoRecordListView.as_view(), name='video_record_list'),
   path('video_records/<int:video_record_id>/', VideoRecordDetailView.as_view(), name='video_record_detail'),
   path('teams/', TeamListCreate.as_view(), name='team-list-create'),
   path('teams/<int:pk>/', TeamDetail.as_view(), name='team-detail'),
   path('teams/<int:team_id>/players/', PlayerListCreate.as_view(), name='player-list-create'),
   path('players/<int:pk>/', PlayerDetail.as_view(), name='player-detail'),
   path('upload/', upload_video, name='upload_video'),
   path('performance/', PerformanceListView.as_view(), name='performance-list'), 
   path('players/<int:player_id>/performances/', PerformanceDetailView.as_view(), name='player-performance-list'),
   path('register/', RegisterView.as_view(), name='register'),  # Endpoint for user registration
   path('users/', UserListView.as_view(), name='all_users'),   # Endpoint to list all users
   path('user/login/', LoginUser.as_view(), name='login'), 
   path('players/', PlayerListView.as_view(), name='player_list'), 
   path('send-invite/', InviteView.as_view(), name='send-invite'),
   path('players/<int:player_id>/', PlayerDetailView.as_view(), name='player_detail'), # Endpoint for user login
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

