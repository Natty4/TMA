from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from .models import Auser, Service, Doctor, Appointment, Feedback
from .forms import AppointmentForm, AuserForm
import requests
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io



def index(request):
    services = Service.objects.all()
    doctors = Doctor.objects.all()
    return render(request, 'index.html', {'services': services, 'doctors': doctors})

def get_services(request):
    service_id = request.GET.get('service')
    if service_id: 
        service = get_object_or_404(Service, id=service_id)
        doctors = service.professionals.all()
        return JsonResponse({
            'service': {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'duration': service.duration,
                'price': service.price,
                'doctors': [{'id': doctor.id, 'full_name': doctor.full_name, 'specialty': doctor.specialty, 'availability': doctor.availability, 'rating': doctor.rating} for doctor in doctors]
            }
        })
    else:
        services = Service.objects.filter(is_active=True)
        return JsonResponse({
            'services': [{'id': service.id, 'name': service.name, 'description': service.description, 'duration': service.duration, 'price': service.price} for service in services]
        })


def get_doctors(request):
    doctors = Doctor.objects.all().values('id', 'full_name', 'specialty', 'availability', 'rating')
    return JsonResponse({'doctors': list(doctors)})

def feedback_page(request):
    return render(request, 'feedback.html')

def book_appointment_page(request):
    return render(request, 'booking_form.html')

def get_completed_appointments(request):
    user_id = request.GET.get('user_id')
    appointments = Appointment.objects.filter(status='completed').values('id', 'doctor__full_name', 'service__name', 'date', 'time')
    return JsonResponse({'appointments': list(appointments)})

import json

@csrf_exempt
@require_POST
def submit_feedback(request):
    try:
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        rating = data.get('rating')
        comments = data.get('comments')

        appointment = Appointment.objects.get(id=appointment_id)
        Feedback.objects.create(appointment=appointment, rating=rating, comments=comments)

        return JsonResponse({'success': True})
    except Appointment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Appointment does not exist'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def book_appointment_step1(request):
    services_d = request.GET.get('service')
    service = get_object_or_404(Service, id=services_d)
    return render(request, 'book_appointment_step1.html', {'service': service})

def book_appointment_step2(request):
    service_id = request.GET.get('service')
    doctor_id = request.GET.get('doctor')
    date = request.GET.get('date')
    time = request.GET.get('time')

    if not (service_id and doctor_id and date and time):
        return JsonResponse({'error': 'Missing required parameters'}, status=400)

    try:
        service = get_object_or_404(Service, id=service_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)
    except (Service.DoesNotExist, Doctor.DoesNotExist):
        return JsonResponse({'error': 'Service or Doctor not found'}, status=404)

    context = {
        'service': service,
        'doctor': doctor,
        'date': date,
        'time': time,
        'form': AuserForm()
    }

    return render(request, 'book_appointment_step2.html', context)

def book_appointment(request):
    if request.method == 'POST':
        form = AuserForm(request.POST)
        if form.is_valid():
            auser = form.save()
            service_id = request.POST.get('service')
            doctor_id = request.POST.get('doctor')
            date = request.POST.get('date')
            time = request.POST.get('time')
            reason_for_appointment = request.POST.get('reason_for_appointment', '')
            notes = request.POST.get('notes', '')

            service = get_object_or_404(Service, id=service_id)
            doctor = get_object_or_404(Doctor, id=doctor_id)

            appointment = Appointment.objects.create(
                user=auser,
                service=service,
                doctor=doctor,
                date=date,
                time=time,
                reason_for_appointment=reason_for_appointment,
                notes=notes,
                amount=service.price
            )
            # Optionally send a confirmation email or notification here
            return redirect(f'/appointment_summary/?appointment_id={appointment.id}')
        else:
            return render(request, 'book_appointment_step2.html', {'form': form, 'error': 'Invalid form submission.'})
    else:
        return redirect('book_appointment_step1')

def appointment_success(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id)
        return render(request, 'appointment_success.html', {'appointment': appointment})
    else:
        appointment_id = request.GET.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id)
        return render(request, 'appointment_success.html', {'appointment': appointment})

def appointment_summary(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # For now, just a placeholder for payment handling
        payment_method = request.POST.get('payment_method')
        if payment_method == 'card':
            # Process card payment (placeholder)
            pass
        elif payment_method == 'cash':
            # Process cash payment (placeholder)
            pass

        # Update the appointment status
        appointment.payment_status = 'paid'
        appointment.save()

        return redirect('appointment_success')
    else:
        appointment_id = request.GET.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id)
        return render(request, 'appointment_summary.html', {'appointment': appointment})
    
    

def generate_invoice(request):
    appointment_id = request.GET.get('appointment_id')
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return HttpResponse("Appointment not found", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{appointment_id}.pdf"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Draw invoice details
    p.drawString(100, height - 100, f"Invoice for Appointment #{appointment_id}")
    p.drawString(100, height - 140, f"Name: {appointment.user.full_name}")
    p.drawString(100, height - 180, f"Email: {appointment.user.email}")
    p.drawString(100, height - 220, f"Phone: {appointment.user.phone_number}")
    p.drawString(100, height - 260, f"Service: {appointment.service.name}")
    p.drawString(100, height - 300, f"Doctor: {appointment.doctor.full_name}")
    p.drawString(100, height - 340, f"Date: {appointment.date.strftime('%Y-%m-%d')}")
    p.drawString(100, height - 380, f"Time: {appointment.time.strftime('%H:%M')}")
    p.drawString(100, height - 420, f"Price: ${appointment.service.price}")
    p.drawString(100, height - 460, f"Payment Status: {appointment.payment_status}")

    p.showPage()
    p.save()

    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()

    response.write(pdf)
    return response



# def book_appointment(request):
#     print('------------------1')
#     if request.method == 'POST':
#         print('------------------2')
#         form = AppointmentForm(request.POST)
#         print(form.data, '>>>>>>>>>>>>')
#         if form.is_valid():
#             print('------------------3')
#             appointment = form.save()
#             # Optionally send a confirmation email or notification here
#             return redirect('appointment_success')  # Redirect to a success page or confirmation page
#         else:
#             return render(request, 'book_appointment.html', {'form': form, 'error': 'Invalid form submission.'})
#     else:
#         return render(request, 'book_appointment.html')


# def appointment_success(request):
#     return render(request, 'appointment_success.html')

# @csrf_exempt
# def book_appointment(request):
#     if request.method == 'POST':
#         user_email = request.POST.get('email')
#         user_name = request.POST.get('name')
#         user_phone = request.POST.get('phone_number')
#         service_id = request.POST.get('service')
#         doctor_id = request.POST.get('doctor')
#         appointment_date = request.POST.get('date')
#         appointment_time = request.POST.get('time')
#         reason = request.POST.get('reason_for_appointment', None)
#         notes = request.POST.get('notes', None)

#         user, created = Auser.objects.get_or_create(email=user_email, defaults={'full_name': user_name, 'phone_number': user_phone})
#         service = get_object_or_404(Service, id=service_id)
#         doctor = get_object_or_404(Doctor, id=doctor_id)

#         appointment = Appointment.objects.create(
#             user=user,
#             service=service,
#             amount=service.price,
#             doctor=doctor,
#             date=appointment_date,
#             time=appointment_time,
#             reason_for_appointment=reason,
#             notes=notes,
#             status='booked'
#         )

#         # send_mail(
#         #     'Appointment Confirmation',
#         #     f'Your appointment for {service.name} with Dr. {doctor.full_name} on {appointment_date} at {appointment_time} has been booked.',
#         #     'clinic@example.com',
#         #     [user_email],
#         #     fail_silently=False,
#         # )

#         return JsonResponse({'status': 'success', 'appointment_id': appointment.id})

#     return JsonResponse({'status': 'fail', 'error': 'Invalid request method'}, status=405)


def get_appointments(request, email):
    user = get_object_or_404(Auser, email=email)
    appointments = Appointment.objects.filter(user=user).values(
        'id', 'service__name', 'doctor__full_name', 'date', 'time', 'status'
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