from django.urls import path
from .views import TeamListCreate, TeamDetail, PlayerListCreate, PlayerDetail

urlpatterns = [
    path('teams/', TeamListCreate.as_view(), name='team-list-create'),
    path('teams/<int:pk>/', TeamDetail.as_view(), name='team-detail'),
    path('teams/<int:team_id>/players/', PlayerListCreate.as_view(), name='player-list-create'),
    path('players/<int:pk>/', PlayerDetail.as_view(), name='player-detail'),
]