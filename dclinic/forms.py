from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['user', 'service', 'doctor', 'date', 'time', 'reason_for_appointment', 'notes', 'payment_method', 'amount']