from django.contrib import admin
from .models import Complex, Organizer, Contract, Employer, Zone, Event, Man, Ticket, Control, Review

admin.site.register([Complex, Organizer, Contract, Employer, Zone, Event, Man, Ticket, Control, Review])