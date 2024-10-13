from django.contrib import admin
from .models import EventRegistration


# Register Registration model
@admin.register(EventRegistration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('participant', 'event')
    search_fields = ('participant__name', 'event__name', 'participant__ambassador_name')
    list_filter = ('event__event_type', 'participant__payment_acknowledgement')
