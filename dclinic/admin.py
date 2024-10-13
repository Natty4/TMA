from django.contrib import admin
from .models import Auser, Appointment, Service, Professional, Business, BusinessOperationalHours, Feedback, ProfessionalAvailability


admin.site.register(Auser)
admin.site.register(Appointment)
admin.site.register(Service)
admin.site.register(Professional)
admin.site.register(Business)
admin.site.register(BusinessOperationalHours)
admin.site.register(Feedback)
admin.site.register(ProfessionalAvailability)