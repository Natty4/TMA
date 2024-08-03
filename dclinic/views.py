from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from .models import Auser, Service, Doctor, Appointment, Feedback



def get_services(request):
    services = Service.objects.all().values('id', 'name', 'price')
    return JsonResponse({'services': list(services)})

def get_doctors(request):
    doctors = Doctor.objects.all().values('id', 'full_name', 'specialty', 'availability', 'rating')
    return JsonResponse({'doctors': list(doctors)})

def index(request):
    services = Service.objects.all()
    doctors = Doctor.objects.all()
    return render(request, 'index.html', {'services': services, 'doctors': doctors})

def appointment(request):
    services = Service.objects.all()
    doctors = Doctor.objects.all()
    return render(request, 'booking_form.html', {'services': services, 'doctors': doctors})

@csrf_exempt
def book_appointment(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        user_name = request.POST.get('name')
        user_phone = request.POST.get('phone_number')
        service_id = request.POST.get('service')
        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('date')
        appointment_time = request.POST.get('time')
        reason = request.POST.get('reason_for_appointment')
        notes = request.POST.get('notes')

        user, created = Auser.objects.get_or_create(email=user_email, defaults={'full_name': user_name, 'phone_number': user_phone})
        service = get_object_or_404(Service, id=service_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)

        appointment = Appointment.objects.create(
            user=user,
            service=service,
            amount=service.price,
            doctor=doctor,
            date=appointment_date,
            time=appointment_time,
            reason_for_appointment=reason,
            notes=notes,
            status='booked'
        )

        # send_mail(
        #     'Appointment Confirmation',
        #     f'Your appointment for {service.name} with Dr. {doctor.full_name} on {appointment_date} at {appointment_time} has been booked.',
        #     'clinic@example.com',
        #     [user_email],
        #     fail_silently=False,
        # )

        return JsonResponse({'status': 'success', 'appointment_id': appointment.id})

    return JsonResponse({'status': 'fail', 'error': 'Invalid request method'}, status=405)

@csrf_exempt
def submit_feedback(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        rating = request.POST.get('rating')
        comments = request.POST.get('comments')

        appointment = get_object_or_404(Appointment, id=appointment_id)
        Feedback.objects.create(
            appointment=appointment,
            rating=rating,
            comments=comments
        )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail', 'error': 'Invalid request method'}, status=405)

def get_appointments(request):
    user_email = request.GET.get('email')
    user = get_object_or_404(Auser, email=user_email)
    appointments = Appointment.objects.filter(user=user).values(
        'id', 'service__name', 'doctor__full_name', 'date', 'time', 'status', 'amount', 'payment_status'
    )
    return JsonResponse({'appointments': list(appointments)})

def update_appointment_status(request, appointment_id, status):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = status
    appointment.save()
    return JsonResponse({'status': 'success', 'new_status': appointment.status})

def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'canceled'
    appointment.save()
    return JsonResponse({'status': 'success'})




# Reminder Notification View
def send_reminder_notifications():
    from django.utils.timezone import now
    from datetime import timedelta
    reminder_time = now() + timedelta(days=1)

    appointments = Appointment.objects.filter(date=reminder_time.date(), time__lte=reminder_time.time())
    for appointment in appointments:
        user = appointment.user
        send_mail(
            'Appointment Reminder',
            f'This is a reminder for your appointment for {appointment.service.name} with {appointment.doctor.full_name} on {appointment.date} at {appointment.time}.',
            'clinic@example.com',
            [user.email],
            fail_silently=False,
        )

        # Send Telegram reminder
        # Assuming you have a field user.telegram_user_id in the User model
        if user.telegram_user_id:
            # Implement Telegram reminder sending here
    #         bot = get_telegram_bot_instance()
    #         bot.send_message(user.telegram_user_id, f'This is a reminder for your appointment for {appointment.service.name} with {appointment.doctor.full_name} on {appointment.date} at {appointment.time}.')
    # return JsonResponse({'status': 'success'})
            pass








# from django.shortcuts import render
# from django.http import JsonResponse
# from .models import Service, Appointment

# def index(request):
#     return render(request, 'index.html')

# def get_services(request):
#     services = Service.objects.all().values('id', 'name')
#     return JsonResponse({'services': list(services)})

# def book_appointment(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         service_id = request.POST.get('service')
#         date = request.POST.get('date')
#         time = request.POST.get('time')
        
#         service = Service.objects.get(id=service_id)
#         appointment = Appointment(name=name, email=email, service=service, date=date, time=time)
#         appointment.save()
#         return JsonResponse({'status': 'success'})
#     return JsonResponse({'status': 'fail'})