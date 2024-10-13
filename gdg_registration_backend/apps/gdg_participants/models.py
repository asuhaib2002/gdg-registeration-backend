from django.db import models

from gdg_registration_backend.apps.gdg_participants.enums import ParticipantStatus, ParticipantType

class Participant(models.Model):
    name = models.CharField(max_length=255)
    email_address = models.EmailField(unique=True)
    cnic = models.CharField(max_length=15)
    phone_number = models.CharField(max_length=15)
    organization = models.CharField(max_length=255, null=True)
    linkedin_url = models.URLField(null=True)
    github_url = models.URLField(null=True)
    participant_type = models.CharField(max_length=50, choices=[(tag.name, tag.value) for tag in ParticipantType], default=ParticipantType.STUDENT.value)
    ambassador_name = models.CharField(max_length=255, null=True)
    participant_status = models.CharField(max_length=20, choices=[(tag.name, tag.value) for tag in ParticipantStatus], default=ParticipantStatus.PENDING.value)
    payment_acknowledgement = models.BooleanField(default=False)
    job_role = models.CharField(max_length=2550, null=True)

    def __str__(self):
        return self.name
