from django.db import models

class Performance(models.Model):
    performance_id = models.AutoField(primary_key=True)
    player_id = models.PositiveSmallIntegerField()
    # player_id = models.ForeignKey(player, on_delete=models.CASCADE)
    passes = models.IntegerField()
    assists = models.IntegerField()
    no_of_goals = models.IntegerField()
    shots_on_target = models.PositiveIntegerField()

    def __str__(self):
        return f"Performance {self.performance_id} for Player {self.player_id}"
