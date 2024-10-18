from django.shortcuts import render

# Create your views here.
from marshmallow import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from gdg_registration_backend.apps.gdg_participants.data_class_model import ShortlistDTO
from .service import RegistrationService
from gdg_registration_backend.apps.gdg_participants.enums import ParticipantStatus

class GetEventListAPI(APIView):

    permission_classes = []

    def get(self, request):
        try:
            page = request.query_params.get("page", 1)
            per_page = request.query_params.get("perPage", 10)
            filter_by = request.query_params.get("filterBy", None)
            search = request.query_params.get("search", None)

            event_type = request.query_params.get("event_type")
            if not event_type:
                return Response(
                    {"error": "event_type query parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            event_dto = RegistrationService.get_event_list(
                event_type, page, per_page, filter_by, search
            )
            return Response(event_dto, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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



class UpdateParticipantStatusAPI(APIView):
    permission_classes = []  # Adjust as needed

    def post(self, request):
        try:
            # Extract necessary data from the request
            event_type = request.data.get("type")
            participant_status = request.data.get("status")
            participants = request.data.get("participants", [])

            # Check if participants are provided
            if not participants:
                return Response(
                    {"error": "No participants provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate if the participant status is a valid value in the ParticipantStatus enum
            if not ParticipantStatus.is_valid_status(participant_status):
                return Response(
                    {"error": f"Invalid participant status: {participant_status}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create a DTO for participants
            shortlist_dto = ShortlistDTO(participants=participants)

            # Call the service to update participants' status and get their names
            updated_participants = RegistrationService.status_participants(
                shortlist_dto, event_type, participant_status
            )

            # Return success response with updated participant names
            return Response(
                {
                    "message": "Participants status updated successfully",
                    "updated_participants": updated_participants
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            # Handle errors (e.g., invalid event or status)
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Catch any unexpected errors
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

        try:
            registration = RegistrationService.register_event(event_type, request.data)
            return Response(
                {
                    "message": "Registration successful",
                    "registration_id": registration.id,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
