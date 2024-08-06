from django.db import models

class Auser(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name
    

class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.IntegerField(help_text='Duration in minutes')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    professionals = models.ManyToManyField('Doctor', related_name='services')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    full_name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=255)
    availability = models.TextField()
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.full_name

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ]

    user = models.ForeignKey(Auser, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
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
        # Format date as "day (number), month (name), year"
        formatted_date = self.date.strftime('%B, %d')
        return f"{self.user.full_name} - {self.service.name} on {formatted_date} at {self.time.strftime('%H:%M')}"
    
    
class Feedback(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Feedback for {self.appointment}"








# from django.db import models

# class Service(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#     duration = models.IntegerField(help_text='Duration in minutes')
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return self.name

# class Appointment(models.Model):
#     name = models.CharField(max_length=255)
#     email = models.EmailField()
#     service = models.ForeignKey(Service, on_delete=models.CASCADE)
#     date = models.DateField()
#     time = models.TimeField()

#     def __str__(self):
#         return f"{self.name} - {self.service.name} on {self.date} at {self.time}"