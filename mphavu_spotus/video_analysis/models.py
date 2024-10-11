from django.db import models

class FootballVideo(models.Model):
    video_file = models.FileField(upload_to='videos/')
    player_name = models.CharField(max_length=20, null=True, blank=True)  # Allow null values
    shooting_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Use DecimalField for precision
    shooting_angle = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Use DecimalField for precision
    player_id = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.video_file.name
