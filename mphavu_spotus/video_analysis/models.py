# analysis/models.py
from django.db import models

class FootballVideo(models.Model):
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    shooting_accuracy = models.FloatField(null=True, blank=True)
    shooting_angle = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.video_file.name
