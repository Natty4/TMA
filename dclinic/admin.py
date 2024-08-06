from django.contrib import admin
from .models import Service, Doctor, Appointment, Feedback, Auser
    
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price',  'duration')
    filter_horizontal = ('professionals',)
    search_fields = ('name', 'professionals__full_name')
    
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialty', 'availability', 'rating')
    
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'doctor', 'date', 'time', 'status')
    
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'rating', 'comments')
    
@admin.register(Auser)
class AuserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number')
    