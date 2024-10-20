from django.db import models

class FootballVideo(models.Model):
    video_file = models.FileField(upload_to='videos/')
    shooting_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    shooting_angle = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    player_id = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.video_file.name
