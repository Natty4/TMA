from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from dclinic.models import Auser, Business, Service, Professional, ProfessionalAvailability, Appointment, Feedback, BusinessOperationalHours, Invoice, Auser
from dclinic.serializers import (
    AuserSerializer,
    BusinessSerializer,
    ServiceSerializer,
    ProfessionalSerializer,
    ProfessionalAvailabilitySerializer,
    AppointmentSerializer,
    AppointmentCreateSerializer,
    FeedbackSerializer,
    InvoiceSerializer,
    
)

class AuserListCreateView(APIView):
    def post(self, request):
        # Extract user data from the request
        user_data = {
            'tg_id': request.data.get('tg_id'),
            'full_name': request.data.get('full_name'),
            'email': request.data.get('email'),
            'passport_id': request.data.get('passport_id'),
            'phone_number': request.data.get('phone_number'),
            'address': request.data.get('address', ''),
        }

        # Validate incoming user data
        serializer = AuserSerializer(data=user_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = user_data['phone_number']

        # Check if the user exists
        try:
            existing_user = Auser.objects.get(phone_number=phone_number)

            # Check for data mismatches
            if (existing_user.full_name != user_data['full_name'] or
                existing_user.email != user_data['email'] or
                existing_user.address != user_data['address']):
                return Response({
                    "error": "This phone number is already in use by another user.",
                    "message": "Please verify if the details provided are correct."
                }, status=status.HTTP_400_BAD_REQUEST)

            # If data matches, return existing user data
            serializer = AuserSerializer(existing_user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Auser.DoesNotExist:
            # If user doesn't exist, create a new one
            auser = Auser.objects.create(**user_data)
            serializer = AuserSerializer(auser)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class BusinessListView(APIView):
    def get(self, request):
        businesses = Business.objects.filter(is_active=True)  # Ensure only active businesses are listed
        serializer = BusinessSerializer(businesses, many=True)
        return Response(serializer.data)

class BusinessDetailView(APIView):
    def get(self, request, pk):
        try:
            business = Business.objects.get(pk=pk)
        except Business.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BusinessSerializer(business)
        return Response(serializer.data)

class BusinessServicesView(APIView):
    def get(self, request, pk):
        try:
            business = Business.objects.get(pk=pk)
        except Business.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        services = Service.objects.filter(business=business, is_active=True)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)

class BusinessProfessionalsView(APIView):
    def get(self, request, pk):
        try:
            business = Business.objects.get(pk=pk)
        except Business.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        professionals = Professional.objects.filter(business=business)
        serializer = ProfessionalSerializer(professionals, many=True)
        return Response(serializer.data)
    
class BusinessServiceProfessionalsView(APIView):
    def get(self, request, business_id, service_id):
        try:
            # Retrieve the specific business
            business = Business.objects.get(pk=business_id)
        except Business.DoesNotExist:
            return Response({'detail': 'Business not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Retrieve the specific service within the business
            service = Service.objects.get(pk=service_id, business=business, is_active=True)
        except Service.DoesNotExist:
            return Response({'detail': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Filter professionals related to both the business and specific service
        professionals = Professional.objects.filter(business=business, services=service)

        # Serialize the data for services and professionals
        service_serializer = ServiceSerializer(service)
        professional_serializer = ProfessionalSerializer(professionals, many=True)
        
        # Return both service and professionals in the response
        return Response({
            'service': service_serializer.data,
            'professionals': professional_serializer.data
        })

class BusinessProfessionalAvailabilityView(APIView):
    def get(self, request, pk, professional_id=None):
        try:
            business = Business.objects.get(pk=pk)
        except Business.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        if professional_id:
            professionals = Professional.objects.filter(id=professional_id)
        else:
            professionals = Professional.objects.filter(business=business)
            
        availabilities = ProfessionalAvailability.objects.filter(professional__in=professionals)
        serializer = ProfessionalAvailabilitySerializer(availabilities, many=True)
        return Response(serializer.data)


class ServiceListView(APIView):
    def get(self, request):
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)

class ServiceDetailView(APIView):
    def get(self, request, pk):
        try:
            service = Service.objects.get(pk=pk)
        except Service.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ServiceSerializer(service)
        return Response(serializer.data)

    
class ServiceProfessionalsView(APIView):
    def get(self, request, pk):
        try:
            service = Service.objects.get(pk=pk)
        except Service.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        professionals = service.professionals.filter(business=service.business)

        # Filter by availability
        date = request.query_params.get('date')
        time = request.query_params.get('time')
        if date and time:
            professionals = professionals.filter(
                availabilities__date=date,
                availabilities__start_time__lte=time,
                availabilities__end_time__gte=time,
                availabilities__is_available=True
            ).distinct()

        # Exclude professionals who already have appointments at this time
        appointments = Appointment.objects.filter(
            service=service, 
            date=date, 
            time=time
        ).values_list('professional_id', flat=True)
        
        professionals = professionals.exclude(id__in=appointments)
        
        serializer = ProfessionalSerializer(professionals, many=True)

        # Adding availability time formatting for frontend clickable buttons
        for prof in serializer.data:
            availabilities = ProfessionalAvailability.objects.filter(
                professional_id=prof['id'],
                date=date
            ).values('start_time', 'end_time')
            prof['available_times'] = [
                f"{availability['start_time']} - {availability['end_time']}" for availability in availabilities
            ]

        return Response(serializer.data)
    

class ProfessionalListView(APIView):
    def get(self, request):
        professionals = Professional.objects.all()
        serializer = ProfessionalSerializer(professionals, many=True)
        return Response(serializer.data)

class ProfessionalDetailView(APIView):
    def get(self, request, pk):
        try:
            professional = Professional.objects.get(pk=pk)
        except Professional.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProfessionalSerializer(professional)
        return Response(serializer.data)

class ProfessionalAvailabilityView(APIView):
    def get(self, request, pk):
        try:
            professional = Professional.objects.get(pk=pk)
        except Professional.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        availabilities = professional.availabilities.all()

        date = request.query_params.get('date')
        if date:
            availabilities = availabilities.filter(date=date)

        serializer = ProfessionalAvailabilitySerializer(availabilities, many=True)
        return Response(serializer.data)


# class AppointmentListView(APIView):
#     def get(self, request):
#         appointments = Appointment.objects.all()
#         serializer = AppointmentSerializer(appointments, many=True)
#         return Response(serializer.data)

class AppointmentListView(APIView):
    def get(self, request):
        # Get query parameters for filtering
        professional_id = request.query_params.get('professional_id')
        business_id = request.query_params.get('business_id')
        service_id = request.query_params.get('service_id')
        
        # Initialize queryset
        appointments = Appointment.objects.all()
        
        # Apply filters based on query parameters if provided
        if professional_id:
            appointments = appointments.filter(professional_id=professional_id)
        if business_id:
            appointments = appointments.filter(business_id=business_id)
        if service_id:
            appointments = appointments.filter(service_id=service_id)
        
        # Serialize and return the filtered queryset
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

class AppointmentDetailView(APIView):
    def get(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)
    
class AppointmentCreateView(APIView):
    def post(self, request):
        # Extract user data from the incoming payload
        user_data = request.data.get('user')
        
        if not isinstance(user_data, dict):
            return Response({"error": "User data must be a valid JSON object."}, status=status.HTTP_400_BAD_REQUEST)

        user_id = user_data.get('id')
        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate user existence
        try:
            user = Auser.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Extract other appointment details
        service_id = request.data.get('service')
        professional_id = request.data.get('professional')
        date = request.data.get('date')
        starting_time = request.data.get('starting_time')
        ending_time = request.data.get('ending_time')
        notes = request.data.get('notes')
        payment_method = request.data.get('payment_method')
        amount = request.data.get('amount')

        # Prepare appointment data
        appointment_data = {
            'user': user.id,
            'service': service_id,
            'professional': professional_id,
            'date': date,
            'starting_time': starting_time,
            'ending_time': ending_time,
            'notes': notes,
            'payment_method': payment_method,
            'amount': amount,
        }
        
        # Check professional availability
        availability_exists = Appointment.objects.filter(
            professional_id=professional_id,
            date=date,
            starting_time__lt=ending_time,
            ending_time__gt=starting_time
        ).exists()
        if availability_exists:
            return Response({"detail": "The professional is not available at this time."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save the appointment
        serializer = AppointmentCreateSerializer(data=appointment_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class GenerateInvoiceView(APIView):
    def post(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(pk=appointment_id)
        except Appointment.DoesNotExist:
            return Response({'detail': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if an invoice already exists for this appointment
        if hasattr(appointment, 'invoice'):
            return Response({'detail': 'Invoice already generated for this appointment.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the amount based on the service or booking fee (adjust logic as needed)
        amount = appointment.service.booking_fee

        # Create and save the invoice
        invoice = Invoice.objects.create(
            appointment=appointment,
            amount=amount,
            status='Pending'
        )

        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class InvoiceDetailView(APIView):
    def get(self, request, appointment_id):
        try:
            invoice = Invoice.objects.get(appointment__id=appointment_id)
        except Invoice.DoesNotExist:
            return Response({'detail': 'Invoice not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)
    
    