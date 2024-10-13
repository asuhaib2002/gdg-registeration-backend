# from asyncio import Event
from django.db import models

from gdg_registration_backend.apps.gdg_participants.models import Participant
from gdg_registration_backend.apps.gdg_events.models import Event


# Create your models here.
class EventRegistration(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    workshop_participation = models.JSONField(null=True)
    team_name = models.CharField(max_length=255, null=True)
    team_members = models.JSONField(null=True)
    purpose_of_participation = models.TextField(null=True)
    google_technologies = models.JSONField(null=True)
    previous_projects = models.TextField(null=True)

    def __str__(self):
        return f"{self.participant.name} - {self.event.name}"
