from django import forms
from .models import Appointment, Auser

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['user', 'service', 'doctor', 'date', 'time', 'reason_for_appointment', 'notes', 'payment_method', 'amount']
        

class AuserForm(forms.ModelForm):
    class Meta:
        model = Auser
        fields = ['full_name', 'email', 'phone_number', 'address']