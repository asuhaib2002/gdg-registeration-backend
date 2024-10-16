from dataclasses import asdict
from typing import Dict, Any, List, Optional
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.core.paginator import Paginator
from functools import wraps
from django.db import transaction

from gdg_registration_backend.apps.gdg_events.models import Event
from gdg_registration_backend.apps.gdg_events.data_class_model import EventDTO
from gdg_registration_backend.apps.gdg_participants.data_class_model import (
    ConferenceParticipantCreateDTO,
    ConferenceParticipantDTO,
    HackathonParticipantCreateDTO,
    HackathonParticipantDTO,
    HackathonTeamMemberDTO,
    ParticipantCreateDTO,
    ParticipantDTO,
    ShortlistDTO,
    WorkshopParticipantCreateDTO,
    WorkshopParticipantDTO,
)
from gdg_registration_backend.apps.gdg_participants.enums import ParticipantStatus
from gdg_registration_backend.apps.gdg_participants.models import Participant
from gdg_registration_backend.apps.gdg_registration.models import EventRegistration
from gdg_registration_backend.apps.gdg_events.enums import EventTypes

def validate_event(func):
    """Decorator to validate event existence and type."""
    @wraps(func)
    def wrapper(cls, event_type: str, *args, **kwargs):
        try:
            event = Event.objects.get(event_type=event_type)
            return func(cls, event_type, *args, **kwargs)
        except Event.DoesNotExist:
            raise ValidationError(f"Event of type {event_type} not found")
    return wrapper

class RegistrationService:
    PARTICIPANT_DTO_MAPPING = {
        EventTypes.WORKSHOP.value: WorkshopParticipantDTO,
        EventTypes.CONFERENCE.value: ConferenceParticipantDTO,
        EventTypes.HACKATHON.value: HackathonParticipantDTO,
    }

    DEFAULT_ORDERING = ['participant__name', 'created_at']

    @classmethod
    def _build_search_query(cls, search: str) -> Q:
        """Build Q object for searching across multiple fields."""
        if not search:
            return Q()
        
        return Q(participant__name__icontains=search) | \
               Q(participant__email_address__icontains=search) | \
               Q(participant__organization__icontains=search) | \
               Q(participant__phone_number__icontains=search)

    @classmethod
    def _apply_filters(cls, queryset, filters: Dict[str, Any]) -> Any:
        """Apply multiple filters to queryset."""
        if not filters:
            return queryset

        # Transform filters to match participant fields
        transformed_filters = {}
        for key, value in filters.items():
            if key == 'participant_status':
                transformed_filters['participant__participant_status'] = value
            elif key.startswith('participant__'):
                transformed_filters[key] = value
            else:
                transformed_filters[f'participant__{key}'] = value

        return queryset.filter(**transformed_filters)

    @classmethod
    @validate_event
    def get_event_list(
        cls,
        event_type: str,
        page: int,
        per_page: int,
        filter_by: Dict[str, Any],
        search: str
    ) -> Dict[str, Any]:
        """Get filtered and paginated event list."""
        try:
            # Start with event registrations and prefetch related participant data
            registrations = EventRegistration.objects.filter(
                event__event_type=event_type
            ).select_related(
                'participant'
            ).order_by(
                *cls.DEFAULT_ORDERING
            )

            # Apply search if provided
            search_query = cls._build_search_query(search)
            if search_query:
                registrations = registrations.filter(search_query)

            # Apply filters
            registrations = cls._apply_filters(registrations, filter_by)

            # Calculate pagination
            try:
                page = int(page)
                per_page = int(per_page)
            except (TypeError, ValueError):
                page = 1
                per_page = 10

            # Ensure positive values
            page = max(1, page)
            per_page = max(1, min(100, per_page))  # Limit max per_page to 100

            # Create paginator with ordered queryset
            paginator = Paginator(registrations, per_page)
            
            # Handle page number exceeding max pages
            total_pages = paginator.num_pages
            if page > total_pages:
                page = total_pages if total_pages > 0 else 1

            page_obj = paginator.get_page(page)

            # Create DTOs for participants
            participant_dtos = [
                cls._create_participant_dto(registration, event_type)
                for registration in page_obj
            ]

            return {
                "event_type": event_type,
                "participants": participant_dtos,
                "pagination": {
                    "total_count": paginator.count,
                    "total_pages": total_pages,
                    "current_page": page,
                    "per_page": per_page,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous()
                }
            }

        except Exception as e:
            raise ValidationError(f"Error fetching event list: {str(e)}")

    @classmethod
    def _create_participant_dto(cls, registration: EventRegistration, event_type: str) -> Any:
        """Create appropriate DTO based on event type."""
        dto_class = cls.PARTICIPANT_DTO_MAPPING.get(event_type)
        if not dto_class:
            raise ValidationError(f"Invalid event type: {event_type}")

        participant = registration.participant
        base_dto_data = {
            "id": participant.id,
            "name": participant.name,
            "email_address": participant.email_address,
            "cnic": participant.cnic,
            "participant_type": participant.participant_type,
            "phone_number": participant.phone_number,
            "organization": participant.organization,
            "linkedin_url": participant.linkedin_url,
            "ambassador_name": participant.ambassador_name,
            "payment_acknowledgement": participant.payment_acknowledgement,
            "status": participant.participant_status,
            "registration_id": registration.id,
            "created_at": registration.created_at.isoformat() if registration.created_at else None,
        }

        if event_type == EventTypes.WORKSHOP.value:
            base_dto_data["workshop_participation"] = registration.workshop_participation
        elif event_type == EventTypes.CONFERENCE.value:
            base_dto_data["job_role"] = participant.job_role
        elif event_type == EventTypes.HACKATHON.value:
            base_dto_data.update({
                "team_name": registration.team_name,
                "team_members": [
                    HackathonTeamMemberDTO(**member)
                    for member in (registration.team_members or [])
                ],
                "purpose_of_participation": registration.purpose_of_participation,
                "google_technologies": registration.google_technologies,
                "previous_projects": registration.previous_projects,
            })

        return dto_class(**base_dto_data)

    @classmethod
    @validate_event
    def get_event_list(
        cls,
        event_type: str,
        page: int,
        per_page: int,
        filter_by: Dict[str, Any],
        search: str
    ) -> Dict[str, Any]:
        """Get filtered and paginated event list."""
        event = Event.objects.get(event_type=event_type)
        
        # Start with all participants
        participants = Participant.objects.all()
        
        # Apply search if provided
        search_query = cls._build_search_query(search)
        if search_query:
            participants = participants.filter(search_query)
        
        # Apply filters
        participants = cls._apply_filters(participants, filter_by)
        
        # Get registrations for filtered participants
        registrations = EventRegistration.objects.filter(
            event=event,
            participant__in=participants
        ).select_related('participant')  # Optimize DB queries

        # Paginate results
        paginator = Paginator(registrations, per_page)
        page_obj = paginator.get_page(page)

        # Create DTOs for participants
        participant_dtos = [
            cls._create_participant_dto(registration, event_type)
            for registration in page_obj
        ]

        return {
            "event_type": event.event_type,
            "participants": participant_dtos,
            "total_count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
        }

    @classmethod
    @validate_event
    def shortlist_participants(cls, shortlist_dto: ShortlistDTO, event_type: str) -> None:
        """Shortlist participants for an event."""
        event = Event.objects.get(event_type=event_type)
        
        # Validate participants exist
        participants = Participant.objects.filter(id__in=shortlist_dto.participants)
        if len(participants) != len(shortlist_dto.participants):
            raise ValidationError("Some participant IDs are invalid")

        # Get registrations
        registrations = EventRegistration.objects.filter(
            event=event,
            participant__in=participants
        ).select_related('participant')

        # Update status in bulk
        Participant.objects.filter(
            id__in=shortlist_dto.participants
        ).update(participant_status=ParticipantStatus.SHORTLISTED.value)

        # TODO: Implement email notification logic here
        # for registration in registrations:
        #     send_shortlist_notification(registration.participant)

    @classmethod
    def register_event(cls, event_type: str, data: Dict[str, Any]) -> EventRegistration:
        """Register participant for an event."""
        # Validate event exists
        event = Event.objects.filter(event_type=event_type).first()
        if not event:
            raise ValidationError(f"Event of type {event_type} not found")

        # Create appropriate DTO based on event type
        participant_dto = cls._create_participant_create_dto(event_type, data)
        
        # Validate participant data
        participant_dto.validate()

        # Check for existing registration
        existing_participant = Participant.objects.filter(
            Q(email_address=participant_dto.email_address) |
            Q(phone_number=participant_dto.phone_number) |
            Q(cnic=participant_dto.cnic)
        ).first()

        if existing_participant:
            if EventRegistration.objects.filter(
                participant=existing_participant,
                event=event
            ).exists():
                raise ValidationError("Participant is already registered for this event")

        # Create or update participant
        participant = cls._create_or_update_participant(participant_dto, existing_participant)

        # Create registration
        registration = cls._create_event_registration(event, participant, data)

        return registration

    @classmethod
    def _create_participant_create_dto(cls, event_type: str, data: Dict[str, Any]) -> Any:
        """Create appropriate CreateDTO based on event type."""
        base_data = {
            "name": data.get("name"),
            "email_address": data.get("email_address"),
            "phone_number": data.get("phone_number"),
            "cnic": data.get("cnic"),
            "registered_as": data.get("registered_as"),
            "organization": data.get("organization", ""),
            "linkedin_url": data.get("linkedin_url", ""),
            "ambassador_name": data.get("ambassador_name", ""),
        }

        if event_type == EventTypes.WORKSHOP.value:
            return WorkshopParticipantCreateDTO(
                **base_data,
                workshop_participation=data.get("workshop_participation", [])
            )
        elif event_type == EventTypes.CONFERENCE.value:
            return ConferenceParticipantCreateDTO(
                **base_data,
                job_role=data["job_role"]
            )
        elif event_type == EventTypes.HACKATHON.value:
            return HackathonParticipantCreateDTO(
                **base_data,
                team_name=data.get("team_name"),
                team_members=data.get("team_members"),
                purpose_of_participation=data.get("purpose_of_participation", ""),
                google_technologies=data.get("google_technologies", []),
                previous_projects=data.get("previous_projects", "")
            )
        else:
            raise ValidationError(f"Invalid event type: {event_type}")

    @classmethod
    def _create_or_update_participant(
        cls,
        participant_dto: ParticipantCreateDTO,
        existing_participant: Optional[Participant] = None
    ) -> Participant:
        """Create or update participant based on DTO."""
        participant_data = {
            "name": participant_dto.name,
            "email_address": participant_dto.email_address,
            "phone_number": participant_dto.phone_number,
            "cnic": participant_dto.cnic,
            "organization": participant_dto.organization,
            "linkedin_url": participant_dto.linkedin_url,
            "ambassador_name": participant_dto.ambassador_name,
        }

        if existing_participant:
            for key, value in participant_data.items():
                setattr(existing_participant, key, value)
            existing_participant.save()
            return existing_participant
        
        return Participant.objects.create(**participant_data)

    @classmethod
    def _create_event_registration(
        cls,
        event: Event,
        participant: Participant,
        data: Dict[str, Any]
    ) -> EventRegistration:
        """Create event registration with additional data."""
        registration_data = {
            "participant": participant,
            "event": event,
            "workshop_participation": data.get("workshop_participation"),
            "team_name": data.get("team_name"),
            "team_members": data.get("team_members"),
            "purpose_of_participation": data.get("purpose_of_participation"),
            "google_technologies": data.get("google_technologies"),
            "previous_projects": data.get("previous_projects"),
        }

        return EventRegistration.objects.create(**registration_data)