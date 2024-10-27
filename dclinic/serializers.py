from rest_framework import serializers
from .models import Auser, Business, BusinessOperationalHours, Service, Professional, ProfessionalAvailability, Appointment, Feedback, Invoice

class AuserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auser
        fields = ['id', 'tg_id', 'full_name', 'email', 'passport_id', 'phone_number', 'address', 'is_active']
        
        
class BusinessOperationalHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessOperationalHours
        fields = ['id', 'day_of_week', 'open_time', 'close_time', 'is_closed']
class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = ['id', 'business', 'full_name', 'role', 'experience_years', 'rating']

class ServiceSerializer(serializers.ModelSerializer):
    professionals = ProfessionalSerializer(many=True)
    business = serializers.StringRelatedField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'duration', 'price', 'professionals', 'business', 'is_active']

class BusinessSerializer(serializers.ModelSerializer):
    operational_hours = BusinessOperationalHoursSerializer(many=True)
    services = ServiceSerializer(many=True)
    class Meta:
        model = Business
        fields = ['id', 'name', 'address', 'phone_number', 'email', 'website', 'is_active', 'operational_hours', 'services']

        
class ProfessionalSerializerDetailed(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    class Meta:
        model = Professional
        fields = ['id', 'business', 'full_name', 'role', 'experience_years', 'rating']

class ProfessionalAvailabilitySerializer(serializers.ModelSerializer):
    professional = ProfessionalSerializer()

    class Meta:
        model = ProfessionalAvailability
        fields = ['id', 'professional', 'date', 'start_time', 'end_time', 'is_available']

class AppointmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    service = ServiceSerializer()
    professional = ProfessionalSerializer()

    class Meta:
        model = Appointment
        fields = [
            'id', 'user', 'service', 'professional', 'date', 'starting_time', 'ending_time', 
            'status', 'reason_for_appointment', 'notes', 'payment_status',
            'payment_method', 'amount', 'transaction_id', 'invoice_number',
            'reschedule_info', 'cancellation_reason'
        ]
class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            'id', 'user', 'service', 'professional', 'date', 'starting_time', 'ending_time', 
            'status', 'reason_for_appointment', 'notes', 'payment_status',
            'payment_method', 'amount', 'transaction_id', 'invoice_number',
            'reschedule_info', 'cancellation_reason'
        ]

class FeedbackSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer()

    class Meta:
        model = Feedback
        fields = ['id', 'appointment', 'rating', 'comments']
        

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'appointment', 'amount', 'status', 'generated_at']