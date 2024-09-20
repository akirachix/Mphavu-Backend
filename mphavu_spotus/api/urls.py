from django.urls import path 
from .views import VideoRecordListView, VideoRecordDetailView
from .views import TeamListCreate, TeamDetail, PlayerListCreate, PlayerDetail

urlpatterns = [
   path('video_records/', VideoRecordListView.as_view(), name='video_record_list'),
   path('video_records/<int:video_record_id>/', VideoRecordDetailView.as_view(), name='video_record_detail'),
    path('teams/', TeamListCreate.as_view(), name='team-list-create'),
    path('teams/<int:pk>/', TeamDetail.as_view(), name='team-detail'),
    path('teams/<int:team_id>/players/', PlayerListCreate.as_view(), name='player-list-create'),
    path('players/<int:pk>/', PlayerDetail.as_view(), name='player-detail'),
]

