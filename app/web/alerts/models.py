from django.db import models
from django.utils import timezone


class Alert(models.Model):
    message = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def is_active(self):
        """ Check if the alert is active based on start and end time """
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def __str__(self):
        return f"Alert: {self.message[:50]}"

    class Meta:
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"
