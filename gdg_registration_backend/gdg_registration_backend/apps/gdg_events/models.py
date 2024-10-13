from django.db import models

from gdg_registration_backend.apps.gdg_events.enums import EventTypes

class Event(models.Model):
    name = models.CharField(max_length=255)
    event_type = models.CharField(max_length=50, choices=[(tag.name, tag.value) for tag in EventTypes])
    description = models.TextField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event_type'], name='unique_event_type'),
            models.CheckConstraint(check=models.Q(event_type__in=[tag.value for tag in EventTypes]), name='valid_event_type')
        ]

    def __str__(self):
        return self.name
