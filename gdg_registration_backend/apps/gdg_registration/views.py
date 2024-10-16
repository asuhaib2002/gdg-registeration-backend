from django.shortcuts import render

# Create your views here.
from marshmallow import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from gdg_registration_backend.apps.gdg_participants.data_class_model import ShortlistDTO
from .service import RegistrationService
import logging

# Set up a logger for this module
logger = logging.getLogger(__name__)

class GetEventListAPI(APIView):
    permission_classes = []

    VALID_FILTER_FIELDS = ['participant_type', 'organization', 'job_role']  # Add more valid filter fields here

    def get(self, request):
        # Get parameters from request
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('perPage', 10))
        event_type = request.query_params.get('event_type')

        # Validate event_type
        if not event_type:
            return Response({"error": "event_type query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate filters
        filter_by = {}
        for param, value in request.query_params.items():
            if param.startswith('filterBy'):
                filter_field = value
                if filter_field not in self.VALID_FILTER_FIELDS:
                    return Response(
                        {"error": f"Invalid filter field '{filter_field}' provided."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if not request.query_params.get(f"search"):
                    return Response(
                        {"error": f"Search parameter is required for filter '{filter_field}'."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filter_by[filter_field] = request.query_params.get(f"search")

        # Call the service method
        try:
            event_dto = RegistrationService.get_event_list(event_type, page, per_page, filter_by)
            return Response(event_dto, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ShortlistParticipantsAPI(APIView):
    permission_classes = []

    def post(self, request):

        try:
            event_type = request.data.get("type")
            participants = request.data.get("participants", [])
            if not participants:
                return Response(
                    {"error": "No participants provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            shortlist_dto = ShortlistDTO(participants=participants)
            RegistrationService.shortlist_participants(shortlist_dto, event_type)
            return Response(
                {"message": "Participants shortlisted successfully"},
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EventRegistrationView(APIView):
    permission_classes = []

    def post(self, request):
        event_type = request.data.get("event_type")
        if not event_type:
            return Response(
                {"error": "Event type is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # try:
        registration = RegistrationService.register_event(event_type, request.data)
        return Response(
            {"message": "Registration successful", "registration_id": registration.id},
            status=status.HTTP_201_CREATED,
        )
        # except ValueError as e:
        #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
