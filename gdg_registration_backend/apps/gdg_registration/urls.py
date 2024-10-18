from django.urls import path
from .views import (
    GetEventListAPI,
    ShortlistParticipantsAPI,
    UpdateParticipantStatusAPI,
    EventRegistrationView,
)

urlpatterns = [
    path("events/list/", GetEventListAPI.as_view(), name="events_list"),
    path(
        "participants/status/update/",
        UpdateParticipantStatusAPI.as_view(),
        name="participants_status_update",
    ),
    path("events/register/", EventRegistrationView.as_view(), name="events_register"),
]
# QR Route to be added
