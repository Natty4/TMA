from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Service, ProfessionalAvailability, BusinessOperationalHours

@receiver(m2m_changed, sender=Service.professionals.through)
def update_professional_availability(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':  # We're interested when a professional is added to a service
        service = instance
        business = service.business
        
        # Create availability for the next 7 days
        days_to_create = 14
        today = timezone.now().date()

        # Get operational hours of the business (for all days of the week)
        operational_hours = BusinessOperationalHours.objects.filter(business=business, is_closed=False)

        # Check if operational hours are set for the business
        if not operational_hours.exists():
            print(f"Operational hours not set for business: {business.name}")
            return  # Exit if no operational hours are found

        for professional_id in pk_set:
            professional = service.professionals.get(pk=professional_id)

            # Loop over the next 7 days
            for day_offset in range(days_to_create):
                future_date = today + timedelta(days=day_offset)
                day_of_week = future_date.weekday()

                # Find the operational hours for the specific day of the week
                business_hours = operational_hours.filter(day_of_week=day_of_week).first()

                if not business_hours:
                    print(f"Business closed on {future_date} for {business.name}. No availability created.")
                    continue  # Skip if the business is closed on this day

                # Check if availability already exists for the professional on that day
                availability_exists = ProfessionalAvailability.objects.filter(
                    professional=professional,
                    date=future_date,
                    start_time=business_hours.open_time,
                    end_time=business_hours.close_time
                ).exists()

                if not availability_exists:
                    # Create new availability
                    ProfessionalAvailability.objects.create(
                        professional=professional,
                        date=future_date,
                        start_time=business_hours.open_time,
                        end_time=business_hours.close_time,
                        is_available=True
                    )
                else:
                    print(f"Availability already exists for {professional.full_name} on {future_date}.")