from django.db import models

class EmailInvite(models.Model):
    email = models.EmailField(unique=True)
    invited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
