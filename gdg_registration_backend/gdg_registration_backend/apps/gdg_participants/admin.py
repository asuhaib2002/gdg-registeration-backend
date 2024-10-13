from django.contrib import admin

from .models import Participant

# Register Participant model
@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_address', 'phone_number', 'cnic', 'participant_type', 'organization', 'participant_status')
    search_fields = ('name', 'email_address', 'cnic', 'phone_number')
    list_filter = ('participant_type', 'participant_status')