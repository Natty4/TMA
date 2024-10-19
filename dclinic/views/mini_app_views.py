from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
import requests
import json
from datetime import timedelta, datetime
from django.conf import settings

API_BASE_URL = settings.API_BASE_URL #"https://zminiapp.vercel.app/api/"


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
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}

    def get_available_slots(business_hours, busy_slots, check_date, service_duration):
        # Get business hours for the specific day
        day_of_week = check_date.strftime("%A")  # Get the day of the week
        if day_of_week not in business_hours:
            return []  # No business hours for this day

        business_start_time, business_end_time = business_hours[day_of_week]
        business_start_minutes = business_start_time.hour * 60 + business_start_time.minute
        business_end_minutes = business_end_time.hour * 60 + business_end_time.minute

        # Create a list to hold all busy minutes
        busy_minutes = []
        duration = service_duration
        # Convert busy slots to minutes
        for busy_slot in busy_slots:
            busy_date = busy_slot[0]  # Access the date using index 0
            start_time = busy_slot[1]  # Access the start time using index 1
            end_time = busy_slot[2]  # Access the end time
            duration =  service_duration # Duration of the service
            if busy_date == check_date.date():  # Check if the busy slot is for the same date
                start_minutes = start_time.hour * 60 + start_time.minute
                end_minutes = end_time.hour * 60 + end_time.minute
                busy_minutes.extend(range(start_minutes, end_minutes))

        busy_minutes = sorted(set(busy_minutes))  # Remove duplicates and sort

        available_slots = []
        
        # Start checking from the business opening hour
        current_time = business_start_minutes

        # Check every minute in the business hours
        while current_time + (service_duration // 60) < business_end_minutes:
            # If the current time is not in the busy schedule and there is enough time for the service
            if all(minute not in busy_minutes for minute in range(current_time, current_time + (service_duration // 60))):
                available_slots.append(datetime.combine(check_date, datetime.min.time()) + timedelta(minutes=current_time))

            # Move to the next minute
            current_time += duration

        return [slot.strftime('%H:%M') for slot in available_slots]

    # Usage of the function
    service_response = requests.get(f'{API_BASE_URL}services/{service_id}/')
    professional_response = requests.get(f'{API_BASE_URL}businesses/{business_id}/professionals/')

    if service_response.status_code == 200 and professional_response.status_code == 200:
        service = service_response.json()
        professionals = professional_response.json()
        appointments = requests.get(f'{API_BASE_URL}appointments/')
        
        for professional in professionals:
            busy_slots = []
            available_slots = {}
            
            if appointments.status_code == 200:
                professional['appointments'] = [appointment for appointment in appointments.json() if appointment['professional']['id'] == professional['id']]
                for appointment in professional['appointments']:
                    date = datetime.strptime(appointment['date'], '%Y-%m-%d').date()
                    start_time = datetime.strptime(appointment['starting_time'], '%H:%M:%S').time()
                    end_time = datetime.strptime(appointment['ending_time'], '%H:%M:%S').time()
                    duration = service['duration']  # Assuming duration is in minutes

                    busy_slots.append((date, start_time, end_time, duration))

                business_hours = {}
                for day in service['business']['operational_hours']:
                    business_hours[days_of_week[day['day_of_week']]] = (
                        datetime.strptime(day['open_time'], '%H:%M:%S').time(),
                        datetime.strptime(day['close_time'], '%H:%M:%S').time()
                    )
                available_slots = get_available_slots(business_hours, busy_slots, datetime.now(), service['duration'])
                professional['available_slots'] = available_slots
                   
                
        return render(request, 'page3.html', {
            'service': service,
            'professionals': professionals,
            'business_id': business_id
        })
    else:
        raise Http404("Service or professionals not found")

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
def thank_you_view(request, appointment_id):
    response = requests.get(f'{API_BASE_URL}appointments/{appointment_id}/')
    if response.status_code == 200:
        appointment = response.json()
        service = appointment['service']
        professional = appointment['professional']
        date = appointment['date']
        time = appointment['starting_time'] + ' - ' + appointment['ending_time']

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





