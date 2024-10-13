from dataclasses import asdict
from rest_framework import status
from rest_framework.response import Response

from gdg_registration_backend.apps.gdg_events.models import Event
from gdg_registration_backend.apps.gdg_events.data_class_model import EventDTO
from gdg_registration_backend.apps.gdg_participants.data_class_model import ConferenceParticipantCreateDTO, ConferenceParticipantDTO, HackathonParticipantCreateDTO, HackathonParticipantDTO, HackathonTeamMemberDTO, ParticipantCreateDTO, ParticipantDTO, ShortlistDTO, WorkshopParticipantCreateDTO, WorkshopParticipantDTO
from gdg_registration_backend.apps.gdg_participants.enums import ParticipantStatus
from gdg_registration_backend.apps.gdg_participants.models import Participant
from gdg_registration_backend.apps.gdg_registration.models import EventRegistration
from gdg_registration_backend.apps.gdg_events.enums import EventTypes


class RegistrationService:

    @staticmethod
    def get_event_list(event_type: str, page: int, per_page: int, filter_by: str, search: str) -> EventDTO:
        event = Event.objects.filter(event_type=event_type).first()
        if not event:
            raise ValueError("Event not found.")

        participants = Participant.objects.all()
        if filter_by and search:
            participants = participants.filter(**{filter_by: search})
        registrations = EventRegistration.objects.filter(event=event, participant__in=participants)
        
        if event_type == EventTypes.WORKSHOP.value:
            participant_dtos = [
                WorkshopParticipantDTO(
                    id=reg.participant.id,
                    name=reg.participant.name,
                    email_address=reg.participant.email_address,
                    cnic=reg.participant.cnic,
                    participant_type=reg.participant.participant_type,
                    phone_number=reg.participant.phone_number,
                    organization=reg.participant.organization,
                    linkedin_url=reg.participant.linkedin_url,
                    ambassador_name=reg.participant.ambassador_name,
                    payment_acknowledgement=reg.participant.payment_acknowledgement,
                    participant_status=reg.participant.participant_status,
                    workshop_participation=reg.workshop_participation
                ) for reg in registrations[page * per_page - per_page: page * per_page]
            ]

        elif event_type == EventTypes.CONFERENCE.value:
            participant_dtos = [
                ConferenceParticipantDTO(
                    id=reg.participant.id,
                    name=reg.participant.name,
                    email_address=reg.participant.email_address,
                    cnic=reg.participant.cnic,
                    participant_type=reg.participant.participant_type,
                    phone_number=reg.participant.phone_number,
                    organization=reg.participant.organization,
                    linkedin_url=reg.participant.linkedin_url,
                    ambassador_name=reg.participant.ambassador_name,
                    payment_acknowledgement=reg.participant.payment_acknowledgement,
                    participant_status=reg.participant.participant_status,
                    job_role=reg.participant.job_role
                ) for reg in registrations[page * per_page - per_page: page * per_page]
            ]

        elif event_type == EventTypes.HACKATHON.value:
            participant_dtos = [
                HackathonParticipantDTO(
                    id=reg.participant.id,
                    name=reg.participant.name,
                    email_address=reg.participant.email_address,
                    cnic=reg.participant.cnic,
                    participant_type=reg.participant.participant_type,
                    phone_number=reg.participant.phone_number,
                    organization=reg.participant.organization,
                    linkedin_url=reg.participant.linkedin_url,
                    ambassador_name=reg.participant.ambassador_name,
                    payment_acknowledgement=reg.participant.payment_acknowledgement,
                    participant_status=reg.participant.participant_status,
                    team_name=reg.team_name,
                    team_members=[
                        HackathonTeamMemberDTO(
                            name=team_member['name'],
                            email_address=team_member.get('email_address'),
                            linkedin_url=team_member.get('linkedin_url'),
                            github_url=team_member.get('github_url', 'N/A'),
                            phone_number=team_member.get('phone_number'),
                            cnic=team_member.get('cnic')
                        ) for team_member in reg.team_members
                    ],
                    purpose_of_participation=reg.purpose_of_participation,
                    google_technologies=reg.google_technologies,
                    previous_projects=reg.previous_projects
                ) for reg in registrations[page * per_page - per_page: page * per_page]
            ]

        else:
            raise ValueError("Invalid event type.")
        event_dto =  EventDTO(event_type=event.event_type, participants=participant_dtos)
        response_data = asdict(event_dto)  # Convert the dataclass to a dictionary

        return response_data


    @staticmethod
    def shortlist_participants(shortlist_dto: ShortlistDTO, event_type: str) -> None:
        participants = Participant.objects.filter(id__in=shortlist_dto.participants)
        event = Event.objects.filter(event_type=event_type).first()
        if not event:
            raise ValueError("Event not found.")
        
        registrations = EventRegistration.objects.filter(event=event, participant__in=participants)
        for registration in registrations:
            registration.participant.participant_status = ParticipantStatus.SHORTLISTED.value
            registration.participant.save()
            # Send email notification here


    @staticmethod
    def register_event(event_type: str, data: dict) -> EventRegistration:
        participant_dto = ParticipantCreateDTO(
            name=data.get('name'),
            email_address=data.get('email_address'),
            phone_number=data.get('phone_number'),
            cnic=data.get('cnic'),
            participant_type=data.get('participant_type'),
            organization=data.get('organization', ''),
            linkedin_url=data.get('linkedin_url', ''),
            ambassador_name=data.get('ambassador_name', '')
        )
        
        # Event-specific logic
        if event_type == EventTypes.WORKSHOP.value:
            workshop_dto = WorkshopParticipantCreateDTO(
                **participant_dto.__dict__,  
                workshop_participation=data.get('workshop_participation', [])
            )
            workshop_dto.validate()
            return RegistrationService._create_registration(event_type, workshop_dto)
        
        elif event_type == EventTypes.CONFERENCE.value:
            conference_dto = ConferenceParticipantCreateDTO(
                **participant_dto.__dict__,  
                job_role=data['job_role']
            )
            conference_dto.validate()
            return RegistrationService._create_registration(event_type, conference_dto)

        elif event_type == EventTypes.HACKATHON.value:
            hackathon_dto = HackathonParticipantCreateDTO(
                **participant_dto.__dict__,  
                team_name=data.get('team_name'),
                team_members=data.get('team_members'),
                purpose_of_participation=data.get('purpose_of_participation', ''),
                google_technologies=data.get('google_technologies', []),
                previous_projects=data.get('previous_projects', '')
            )
            hackathon_dto.validate()
            return RegistrationService._create_registration(event_type, hackathon_dto)

        else:
            raise ValueError("Invalid event type.")
    
    @staticmethod
    def _create_registration(event_type: str, event_dto) -> EventRegistration:
        event = Event.objects.get(event_type=event_type)

        participant, created = Participant.objects.get_or_create(
            name=event_dto.name,
            email_address=event_dto.email_address,
            phone_number=event_dto.phone_number,
            cnic=event_dto.cnic,
            organization=event_dto.organization,
            linkedin_url=event_dto.linkedin_url,
            ambassador_name=event_dto.ambassador_name
        )

        # if event_type != EventTypes.WORKSHOP.value:
        if EventRegistration.objects.filter(participant=participant, event=event).exists():
            raise ValueError("Participant is already registered for this event.")

        registration = EventRegistration.objects.create(
            participant=participant,
            event=event,
            workshop_participation=getattr(event_dto, 'workshop_participation', None),
            team_name=getattr(event_dto, 'team_name', None),
            team_members=getattr(event_dto, 'team_members', None),
            purpose_of_participation=getattr(event_dto, 'purpose_of_participation', None),
            google_technologies=getattr(event_dto, 'google_technologies', None),
            previous_projects=getattr(event_dto, 'previous_projects', None)
        )

        return registration