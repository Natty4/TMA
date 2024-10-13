# utils.py
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
from datetime import datetime, timedelta

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None



def get_available_time_slots(doctor, date):
    # Sample logic: Assume the doctor is available from 9 AM to 5 PM with 30-minute slots
    start_time = datetime.combine(date, datetime.strptime("09:00", "%H:%M").time())
    end_time = datetime.combine(date, datetime.strptime("17:00", "%H:%M").time())
    delta = timedelta(minutes=30)

    available_slots = []
    while start_time < end_time:
        # Check if the doctor is available for this slot
        if check_availability(doctor, date, start_time.time()):
            available_slots.append(start_time.strftime("%H:%M"))
        start_time += delta

    return available_slots