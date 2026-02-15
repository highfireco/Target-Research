from django.db import models
from django.utils import timezone
from datetime import timedelta


class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    pin = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
