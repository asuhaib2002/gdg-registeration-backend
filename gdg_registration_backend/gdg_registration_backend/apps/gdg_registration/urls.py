from django.urls import path
from .views import GetEventListAPI, ShortlistParticipantsAPI, EventRegistrationView

urlpatterns = [
    path('get-event-list', GetEventListAPI.as_view(), name='get_event_list'),
    path('shortlist-participants', ShortlistParticipantsAPI.as_view(), name='shortlist_participants'),
    path('event/register/', EventRegistrationView.as_view(), name='event-register'),
]
