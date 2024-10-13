from django.contrib import admin
from .models import  Event

# Register Event model
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'description')
    search_fields = ('name', 'event_type')
    list_filter = ('event_type',)

