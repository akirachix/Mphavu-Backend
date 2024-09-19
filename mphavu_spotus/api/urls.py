from django.urls import path 
from .views import VideoRecordListView, VideoRecordDetailView

urlpatterns = [
   path('video_records/', VideoRecordListView.as_view(), name='video_record_list'),
   path('video_records/<int:video_record_id>/', VideoRecordDetailView.as_view(), name='video_record_detail'),
]
