import os
from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
import requests
import json
import time
import logging
from datetime import timedelta, datetime
from django.conf import settings

# Set up logging
logger = logging.getLogger(__name__)

#API_BASE_URL = settings.API_BASE_URL
API_BASE_URL = os.getenv('API_BASE_URL', 'https://zminiapp.vercel.app/api/')


def home_view(request):
    return render(request, 'index.html')
# Page 1: Business Listing
def business_list_view(request):
    response = requests.get(f'{API_BASE_URL}businesses/')
    if response.status_code == 200:
        businesses = response.json()
        num_services = {}
        for business in businesses:
            business['num_services'] = 0
            response = requests.get(f'{API_BASE_URL}businesses/{business["id"]}/services/')
            if response.status_code == 200:
                services = response.json()
                business['num_services'] = len(services)
        return render(request, 'page1.html', {'businesses': businesses})
    else:
        raise Http404("Businesses not found")
    

# Page 2: Service Listing for a Selected Business
def service_list_view(request, business_id):
    response = requests.get(f'{API_BASE_URL}businesses/{business_id}/services/')
    if response.status_code == 200:
        services = response.json()
        business = services[0]['business']
        return render(request, 'page2.html', {'services': services, 'business': business})
    else:
        raise Http404("Services not found")

# Page 3: Service Details and Professional Availability
def service_detail_view(request, business_id, service_id):
    days_of_week = {
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday',
        3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
    }

    def get_available_slots(business_hours, busy_slots, check_date, service_duration):
        # Function logic remains the same...
        day_of_week = check_date.strftime("%A")
        if day_of_week not in business_hours:
            return []

        business_start, business_end = business_hours[day_of_week]
        business_start_minutes = business_start.hour * 60 + business_start.minute
        business_end_minutes = business_end.hour * 60 + business_end.minute

        busy_minutes_ranges = [
            (start.hour * 60 + start.minute, end.hour * 60 + end.minute)
            for date, start, end, _ in busy_slots if date == check_date.date()
        ]

        available_slots = []
        for start_minute in range(business_start_minutes, business_end_minutes, service_duration):
            end_minute = start_minute + service_duration
            if all(end_minute <= busy_start or start_minute >= busy_end for busy_start, busy_end in busy_minutes_ranges):
                slot_time = datetime.combine(check_date, datetime.min.time()) + timedelta(minutes=start_minute)
                available_slots.append(slot_time.strftime('%H:%M'))

        return available_slots

    # Log the time taken for each API request
    def timed_request(url):
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"API request to {url} took {elapsed_time:.2f} seconds")
        return response

    # Fetch data for the service and professionals
    service_response = timed_request(f'{API_BASE_URL}services/{service_id}/')
    if service_response.status_code != 200:
        raise Http404("Service not found")

    # Retrieve business and professionals in one call
    professionals_response = timed_request(f'{API_BASE_URL}businesses/{business_id}/services/{service_id}/professionals/')
    if professionals_response.status_code != 200:
        raise Http404("Professionals not found")

    data = professionals_response.json()
    service = service_response.json()
    professionals = data.get('professionals', [])

    # Retrieve and cache business hours for the business
    cache_key = f'business_hours_{business_id}'
    business_hours = cache.get(cache_key)
    if not business_hours:
        business_hours = {}
        for day in service['business']['operational_hours']:
            business_hours[days_of_week[day['day_of_week']]] = (
                datetime.strptime(day['open_time'], '%H:%M:%S').time(),
                datetime.strptime(day['close_time'], '%H:%M:%S').time()
            )
        cache.set(cache_key, business_hours, timeout=86400)

    # Process each professional's availability by fetching only their appointments
    for professional in professionals:
        busy_slots = []
        
        # Fetch only the relevant appointments for this professional
        appointment_response = timed_request(f'{API_BASE_URL}appointments/?professional_id={professional["id"]}')
        if appointment_response.status_code == 200:
            appointments = appointment_response.json()
            for appointment in appointments:
                date = datetime.strptime(appointment['date'], '%Y-%m-%d').date()
                start_time = datetime.strptime(appointment['starting_time'], '%H:%M:%S').time()
                end_time = datetime.strptime(appointment['ending_time'], '%H:%M:%S').time()
                busy_slots.append((date, start_time, end_time, service['duration']))

            available_slots = get_available_slots(business_hours, busy_slots, datetime.now(), service['duration'])
            professional['available_slots'] = available_slots
        else:
            professional['available_slots'] = []

    return render(request, 'page3.html', {
        'service': service,
        'professionals': professionals,
        'business_id': business_id
    })

# Page 4: User Information Form
def booking_form_view(request, business_id, service_id, professional_id, date, time):
    professional_response = requests.get(f'{API_BASE_URL}professionals/{professional_id}/')
    service_response = requests.get(f'{API_BASE_URL}services/{service_id}/')
    professional = professional_response.json()
    service = service_response.json()
    if request.method == 'POST':
        user_data = {
            'tg_id': request.POST.get('tg_id', ''),
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'phone_number': request.POST.get('phone_number'),
            'passport_id': request.POST.get('passport_id', ''),
            'address': request.POST.get('address', ''),
            'notes': request.POST.get('notes', '')
        }
        user_response = requests.post(f'{API_BASE_URL}users/', data=user_data)
        if user_response.status_code == 201:
            user_data = user_response.json()
            user_data['notes'] = request.POST.get('notes', '')
        else:
            error_message = user_response.json().get('error') if user_response.json().get('error') else user_response.json()
            return render(request, 'page4.html', {
                'professional': professional,
                'service': service,
                'date': date,
                'time': f"{time} - {(timedelta(minutes=service['duration']) + datetime.strptime(time, '%H:%M')).strftime('%H:%M')}",
                'error_message': error_message, 'user_data': user_data })
        request.session['user_data'] = user_data
        return redirect('booking_summary', business_id=business_id, service_id=service_id,
                        professional_id=professional_id, date=date, time=time)
    
    
    
    if professional_response.status_code == 200 and service_response.status_code == 200:
        return render(request, 'page4.html', {
            'professional': professional,
            'service': service,
            'date': date,
            'time': f"{time} - {(timedelta(minutes=service['duration']) + datetime.strptime(time, '%H:%M')).strftime('%H:%M')}"
        })
    else:
        raise Http404("Service or professional not found")

# Page 5: Booking Summary and Payment Options
def booking_summary_view(request, business_id, service_id, professional_id, date, time):
    user_data = request.session.get('user_data')
    if not user_data:
        return redirect('booking_form', business_id=business_id, service_id=service_id, 
                        professional_id=professional_id, date=date, time=time)

    service_response = requests.get(f'{API_BASE_URL}services/{service_id}/')
    professional_response = requests.get(f'{API_BASE_URL}professionals/{professional_id}/')

    if service_response.status_code == 200 and professional_response.status_code == 200:
        service = service_response.json()
        professional = professional_response.json()
    else:
        raise Http404("Service or professional not found")
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        service_duration = service['duration']
        start_time_dt = datetime.strptime(time, '%H:%M')
        end_time_dt = start_time_dt + timedelta(minutes=service_duration)

        # Create the appointment via the API
        appointment_data = {
            'user': user_data,
            'service': service_id,
            'professional': professional_id,
            'date': date,
            'starting_time': start_time_dt.strftime('%H:%M:%S'),
            'ending_time': end_time_dt.strftime('%H:%M:%S'),
            'notes': user_data.get('notes', ''),
            'payment_method': payment_method,
            'amount': service['price']  
        }

        # Send the request as JSON
        response = requests.post(
            f'{API_BASE_URL}appointments/schedule/',
            data=json.dumps(appointment_data),
            headers={'Content-Type': 'application/json'}  # Set the content type to JSON
        )
        if response.status_code == 201:
            appointment = response.json()
            request.session['booking_successful'] = True    
            return redirect('thank_you', appointment_id=appointment['id'])
        else:
            error_message = response.json().get('error', 'Error creating appointment')
            return render(request, 'page4.html', {
                'service': service_id,
                'professional': professional_id,
                'user_data': user_data,
                'date': date,
                'starting_time': start_time_dt.strftime('%H:%M'),
                'ending_time': end_time_dt.strftime('%H:%M'),
                'error_message': error_message
            })
    return render(request, 'page5.html', {
        'service': service,
        'professional': professional,
        'user_data': user_data,
        'date': date,
        'time': time
    })

# Page 6: Thank You Page
# this view can only be accessed after a successful booking

def thank_you_view(request, appointment_id):
    if not request.session.get('booking_successful'):
        return redirect('home')
    
    response = requests.get(f'{API_BASE_URL}appointments/{appointment_id}/')
    if response.status_code == 200:
        appointment = response.json()
        service = appointment['service']
        professional = appointment['professional']
        date = appointment['date']
        time = appointment['starting_time'] + ' - ' + appointment['ending_time']

        del request.session['booking_successful']
        return render(request, 'page6.html', {
            'appointment': appointment,
            'service': service,
            'professional': professional,
            'date': date,
            'time': time
        })
    else:
        return render(request, 'page6.html', {'error': 'Appointment not found'})



def view_invoice(request, appointment_id):
    # Fetch appointment details to generate the invoice
    appointment_response = requests.get(f'{API_BASE_URL}appointments/{appointment_id}/')

    if appointment_response.status_code == 200:
        appointment = appointment_response.json()
    else:
        raise Http404("Appointment not found")

    # Optional: Format data for a better invoice layout if needed
    service_response = requests.get(f'{API_BASE_URL}services/{appointment["service"]}/')
    professional_response = requests.get(f'{API_BASE_URL}professionals/{appointment["professional"]}/')

    if service_response.status_code == 200 and professional_response.status_code == 200:
        service = service_response.json()
        professional = professional_response.json()
    else:
        raise Http404("Service or professional not found for the invoice")

    return render(request, 'invoice.html', {
        'appointment': appointment,
        'service': service,
        'professional': professional,
    })





