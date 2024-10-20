from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone



class Auser(models.Model):
    tg_id = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    passport_id = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name
    
class Business(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class BusinessOperationalHours(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='operational_hours')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('business', 'day_of_week')

    def __str__(self):
        day = dict(self.DAYS_OF_WEEK)[self.day_of_week]
        return f"{self.business.name} - {day}: {'Closed' if self.is_closed else f'{self.open_time} to {self.close_time}'}"

class Service(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.IntegerField(help_text='Duration in minutes')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    professionals = models.ManyToManyField('Professional', related_name='services')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Professional(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='professionals')
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)  # e.g., 'Doctor', 'Therapist', 'Beautician'
    experience_years = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    def __str__(self):
        return self.full_name

class ProfessionalAvailability(models.Model):
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('professional', 'date', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.professional.full_name} - {self.date} from {self.start_time} to {self.end_time}"

    def is_within_business_hours(self):
        business_hours = BusinessOperationalHours.objects.filter(
            business=self.professional.business,
            day_of_week=int(self.date.weekday()),
            is_closed=False
        ).first()
        if business_hours:
            return (self.start_time >= business_hours.open_time and self.end_time <= business_hours.close_time)
        return False

    def is_overlapping(self):
        return ProfessionalAvailability.objects.filter(
            professional=self.professional,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exists()

    def clean(self):
        """Custom validation logic goes here. This method is called before saving the model."""
        # Check if the availability is within business hours
        # if not self.is_within_business_hours():
        #     raise ValidationError(
        #         _("The availability for %(professional)s on %(date)s must be within business hours."),
        #         params={'professional': self.professional.full_name, 'date': self.date},
        #     )
        
        # Check for overlapping availability
        if self.is_overlapping():
            raise ValidationError(
                _("The availability for %(professional)s on %(date)s from %(start_time)s to %(end_time)s overlaps with another availability."),
                params={
                    'professional': self.professional.full_name,
                    'date': self.date,
                    'start_time': self.start_time,
                    'end_time': self.end_time
                },
            )
        
        # Ensure that the start time is before the end time
        if self.start_time >= self.end_time:
            raise ValidationError(
                _("The start time %(start_time)s must be before the end time %(end_time)s."),
                params={'start_time': self.start_time, 'end_time': self.end_time}
            )

    def save(self, *args, **kwargs):
        # Call the clean method to perform validation before saving
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Prevent deletion of past availability
        if self.date < timezone.now().date():
            raise ValidationError(
                _("Cannot delete availability for a past date: %(date)s."),
                params={'date': self.date}
            )
        super().delete(*args, **kwargs)
    

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ]

    user = models.ForeignKey(Auser, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    starting_time = models.TimeField(default='00:00:00')
    ending_time = models.TimeField(default='00:00:00')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='booked')
    reason_for_appointment = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    payment_status = models.CharField(max_length=20, default='unpaid')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    invoice_number = models.CharField(max_length=255, blank=True, null=True)
    reschedule_info = models.TextField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id} - {self.user.full_name}"

class Feedback(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Feedback for {self.appointment}"
    

class Invoice(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="invoice")
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Booking fee or total amount
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Paid', 'Paid')])
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.id} for Appointment {self.appointment.id}"