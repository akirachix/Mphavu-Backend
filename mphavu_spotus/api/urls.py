from django.urls import path 
from .views import VideoRecordListView, VideoRecordDetailView
from .views import TeamListCreate, TeamDetail, PlayerListCreate, PlayerDetail
from .views import PerformanceListView, PerformanceDetailView

urlpatterns = [
   path('video_records/', VideoRecordListView.as_view(), name='video_record_list'),
   path('video_records/<int:video_record_id>/', VideoRecordDetailView.as_view(), name='video_record_detail'),
   path('teams/', TeamListCreate.as_view(), name='team-list-create'),
   path('teams/<int:pk>/', TeamDetail.as_view(), name='team-detail'),
   path('teams/<int:team_id>/players/', PlayerListCreate.as_view(), name='player-list-create'),
   path('players/<int:pk>/', PlayerDetail.as_view(), name='player-detail'),
   path('performance/', PerformanceListView.as_view(), name='performance-list'), 
   path('players/<int:player_id>/performances/', PerformanceDetailView.as_view(), name='player-performance-list'),
]

