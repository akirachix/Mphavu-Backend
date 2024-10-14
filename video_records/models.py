from django.db import models  

class VideoRecord(models.Model):
   video_record_id = models.AutoField(primary_key=True)
   player_id = models.PositiveSmallIntegerField() 
   video_description = models.TextField() 
   video_file = models.FileField(upload_to='videos/', null=True, blank=True)
   shooting_accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
   shooting_angle = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
   def __str__(self):
      return f"VideoRecord {self.video_record_id} by {self.player_id}"
