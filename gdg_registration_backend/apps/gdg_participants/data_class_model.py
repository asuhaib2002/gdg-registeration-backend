from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import dataclass_json
from marshmallow import ValidationError

# Base Participant DTO
@dataclass
class ParticipantDTO:
    id: int
    name: str
    email_address: str
    cnic: str
    participant_type: str
    phone_number: str
    organization: str
    linkedin_url: str
    ambassador_name: str
    payment_acknowledgement: bool
    participant_status: str

# Workshop Participant DTO
@dataclass
class WorkshopParticipantDTO(ParticipantDTO):
    workshop_participation: List[str]

# Conference Participant DTO
@dataclass
class ConferenceParticipantDTO(ParticipantDTO):
    job_role: str

# Hackathon Team Member DTO
@dataclass
class HackathonTeamMemberDTO:
    name: str
    email_address: str
    linkedin_url: str
    github_url: str
    phone_number: str
    cnic: str

# Hackathon Participant DTO (inherits from ParticipantDTO)
@dataclass
class HackathonParticipantDTO(ParticipantDTO):
    team_name: str
    team_members: List[HackathonTeamMemberDTO]
    purpose_of_participation: str
    google_technologies: List[str]
    previous_projects: str

@dataclass
class ShortlistDTO:
    participants: List[int]

@dataclass_json
@dataclass
class ParticipantCreateDTO:
    name: str
    email_address: str
    cnic: str
    participant_type: str
    phone_number: str
    organization: str
    linkedin_url: str
    ambassador_name: str
    job_role: str

    def validate(self):
        """ Validates common participant fields. """
        errors = []
        if not self.name:
            errors.append("Name is required")
        if not self.email_address:
            errors.append("Email address is required")
        if not self.phone_number:
            errors.append("Phone number is required")
        if not self.cnic:
            errors.append("CNIC is required")
        if not self.participant_type:
            errors.append("Participant type is required")
        if not self.job_role:
            errors.append("Job Role is required")
        if errors:
            raise ValueError(errors)

@dataclass_json
@dataclass
class WorkshopParticipantCreateDTO(ParticipantCreateDTO):
    workshop_participation: List[str] = field(default_factory=list)

    def validate(self):
        """ Validates fields specific to workshop participation. """
        super().validate()
        if not self.workshop_participation:
            raise ValueError("At least one workshop participation is required")


# Conference Participant DTO
@dataclass_json
@dataclass
class ConferenceParticipantCreateDTO(ParticipantCreateDTO):
    job_role: str = ''

    def validate(self):
        """ Validates fields specific to conference participation. """
        super().validate()
        if not self.job_role:
            raise ValueError("Job role is required for conference registration")

# Hackathon Participant DTO (inherits from ParticipantDTO)
@dataclass_json
@dataclass
class HackathonParticipantCreateDTO(ParticipantCreateDTO):
    team_name: str = ''
    team_members: List[dict] = field(default_factory=list)
    purpose_of_participation: str = ''
    google_technologies: List[str] = field(default_factory=list)
    previous_projects: str = ''

    def validate(self):
        """ Validates fields specific to hackathon participation. """
        super().validate()
        if not (2 <= len(self.team_members) <= 4):
            raise ValidationError("Team must consist of at least 2 and at most 4 members.")
        for member in self.team_members:
            if 'name' not in member or 'email_address' not in member or 'linkedin_url' not in member or 'github_url' not in member or 'phone_number' not in member or 'cnic' not in member:
                raise ValidationError("Each team member must have 'name', 'email_address', 'linkedin_url', 'github_url', 'phone_number', 'cnic' .")
        if not self.team_name:
            raise ValueError("Team name is required for hackathon registration")
        if not self.team_members:
            raise ValueError("At least one team member is required")
        if not self.purpose_of_participation:
            raise ValueError("Purpose of participation is required")