from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import VideoRecord
from api.serializers import VideoRecordSerializer
from django.core.files.uploadedfile import SimpleUploadedFile

class VideoRecordDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.video_record = VideoRecord.objects.create(
            player_id=1,
            video_description='Test video description',
            video_file=SimpleUploadedFile(name='test_video.mp4', content=b'test content', content_type='video/mp4'),
            shooting_accuracy=85.5,
            shooting_angle=45.0
        )
        self.url = reverse('video_record_detail', args=[self.video_record.video_record_id])
        

    def test_get_video_record(self):
        """Test the GET method of VideoRecordDetailView"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = VideoRecordSerializer(self.video_record)
        self.assertEqual(response.data, serializer.data)

    def test_put_video_record(self):
        """Test the PUT method of VideoRecordDetailView"""
        updated_data = {
            'player_id': 1,
            'video_description': 'Updated video description',
            'video_file': SimpleUploadedFile(name='updated_video.mp4', content=b'new content', content_type='video/mp4'),
            'shooting_accuracy': 90.0,
            'shooting_angle': 50.0
        }
        response = self.client.put(self.url, updated_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.video_record.refresh_from_db()
        self.assertEqual(self.video_record.video_description, 'Updated video description')
        self.assertTrue(self.video_record.video_file.name.startswith('videos/'))

    def test_delete_video_record(self):
        """Test the DELETE method of VideoRecordDetailView"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(VideoRecord.objects.filter(pk=self.video_record.video_record_id).exists())