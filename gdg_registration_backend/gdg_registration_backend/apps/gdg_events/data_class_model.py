from dataclasses import dataclass
from typing import List, Optional

from gdg_registration_backend.apps.gdg_participants.data_class_model import ParticipantDTO

@dataclass
class EventDTO:
    event_type: str
    participants: List[ParticipantDTO]
