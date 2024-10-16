from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from typing import Dict, Any, List
from dataclasses import dataclass
from functools import wraps

from gdg_registration_backend.apps.gdg_participants.data_class_model import ShortlistDTO
from gdg_registration_backend.apps.gdg_events.enums import EventTypes
from .service import RegistrationService

def validate_event_type(event_type: str) -> bool:
    """Validate if the event type is supported."""
    return event_type in [e.value for e in EventTypes]

def validate_pagination_params(page: int, per_page: int) -> tuple:
    """Validate and convert pagination parameters."""
    try:
        page = int(page)
        per_page = int(per_page)
        if page < 1 or per_page < 1:
            raise ValueError
        return page, per_page
    except (ValueError, TypeError):
        raise ValidationError("Invalid pagination parameters")

def parse_filter_params(filter_by: str) -> Dict[str, Any]:
    """Parse and validate filter parameters."""
    if not filter_by:
        return {}
    
    try:
        filter_dict = {}
        # Split multiple filters (format: field1:value1,field2:value2)
        filters = filter_by.split(',')
        
        for f in filters:
            if ':' not in f:
                continue
            field, value = f.split(':', 1)
            
            # Handle special filter cases
            if field == 'status':
                filter_dict['participant_status'] = value
            elif field == 'organization':
                filter_dict['organization__icontains'] = value
            elif field in ['name', 'email_address', 'phone_number']:
                filter_dict[f'{field}__icontains'] = value
            
        return filter_dict
    except Exception as e:
        raise ValidationError(f"Invalid filter format: {str(e)}")

def api_error_handler(func):
    """Decorator to handle API exceptions consistently."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper

class GetEventListAPI(APIView):
    permission_classes = []

    @api_error_handler
    def get(self, request):
        # Validate event type
        event_type = request.query_params.get('event_type')
        if not event_type or not validate_event_type(event_type):
            raise ValidationError("Invalid or missing event type")

        # Validate and parse pagination
        page, per_page = validate_pagination_params(
            request.query_params.get('page', 1),
            request.query_params.get('perPage', 10)
        )

        # Parse filters
        filter_params = parse_filter_params(request.query_params.get('filterBy'))
        
        # Get search parameter
        search = request.query_params.get('search', '').strip()

        event_dto = RegistrationService.get_event_list(
            event_type=event_type,
            page=page,
            per_page=per_page,
            filter_by=filter_params,
            search=search
        )
        
        return Response(event_dto, status=status.HTTP_200_OK)

class ShortlistParticipantsAPI(APIView):
    permission_classes = []

    @api_error_handler
    def post(self, request):
        event_type = request.data.get('type')
        if not validate_event_type(event_type):
            raise ValidationError("Invalid event type")

        participants = request.data.get('participants', [])
        if not participants or not isinstance(participants, list):
            raise ValidationError("Invalid or empty participants list")

        shortlist_dto = ShortlistDTO(participants=participants)
        RegistrationService.shortlist_participants(shortlist_dto, event_type)
        
        return Response(
            {"message": "Participants shortlisted successfully"},
            status=status.HTTP_200_OK
        )

class EventRegistrationView(APIView):
    permission_classes = []

    @api_error_handler
    def post(self, request):
        event_type = request.data.get('event_type')
        if not validate_event_type(event_type):
            raise ValidationError("Invalid event type")

        # Validate required fields based on event type
        required_fields = {
            EventTypes.WORKSHOP.value: ['name', 'email_address', 'phone_number', 'cnic', 'workshop_participation'],
            EventTypes.CONFERENCE.value: ['name', 'email_address', 'phone_number', 'cnic', 'job_role'],
            EventTypes.HACKATHON.value: ['name', 'email_address', 'phone_number', 'cnic', 'team_name', 'team_members']
        }

        missing_fields = [
            field for field in required_fields[event_type]
            if not request.data.get(field)
        ]

        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

        registration = RegistrationService.register_event(event_type, request.data)
        
        return Response(
            {
                "message": "Registration successful",
                "registration_id": registration.id
            },
            status=status.HTTP_201_CREATED
        )