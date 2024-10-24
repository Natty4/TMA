# Generated by Django 5.0.7 on 2024-08-24 20:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Auser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("full_name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("phone_number", models.CharField(max_length=15)),
                ("address", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Business",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("address", models.TextField()),
                ("phone_number", models.CharField(max_length=15)),
                ("email", models.EmailField(max_length=254)),
                ("website", models.URLField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("time", models.TimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("booked", "Booked"),
                            ("confirmed", "Confirmed"),
                            ("completed", "Completed"),
                            ("canceled", "Canceled"),
                        ],
                        default="booked",
                        max_length=10,
                    ),
                ),
                ("reason_for_appointment", models.TextField(blank=True, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                ("payment_status", models.CharField(default="unpaid", max_length=20)),
                (
                    "payment_method",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "transaction_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "invoice_number",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("reschedule_info", models.TextField(blank=True, null=True)),
                ("cancellation_reason", models.TextField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="dclinic.auser"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Feedback",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rating",
                    models.IntegerField(
                        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
                    ),
                ),
                ("comments", models.TextField(blank=True, null=True)),
                (
                    "appointment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dclinic.appointment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Professional",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("full_name", models.CharField(max_length=255)),
                ("role", models.CharField(max_length=255)),
                ("experience_years", models.IntegerField(default=0)),
                (
                    "rating",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=3),
                ),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="professionals",
                        to="dclinic.business",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="appointment",
            name="professional",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="dclinic.professional"
            ),
        ),
        migrations.CreateModel(
            name="ProfessionalAvailability",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("is_available", models.BooleanField(default=True)),
                (
                    "professional",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="availabilities",
                        to="dclinic.professional",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("duration", models.IntegerField(help_text="Duration in minutes")),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="services",
                        to="dclinic.business",
                    ),
                ),
                (
                    "professionals",
                    models.ManyToManyField(
                        related_name="services", to="dclinic.professional"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="appointment",
            name="service",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="dclinic.service"
            ),
        ),
        migrations.CreateModel(
            name="BusinessOperationalHours",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "day_of_week",
                    models.IntegerField(
                        choices=[
                            (0, "Monday"),
                            (1, "Tuesday"),
                            (2, "Wednesday"),
                            (3, "Thursday"),
                            (4, "Friday"),
                            (5, "Saturday"),
                            (6, "Sunday"),
                        ]
                    ),
                ),
                ("open_time", models.TimeField()),
                ("close_time", models.TimeField()),
                ("is_closed", models.BooleanField(default=False)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="operational_hours",
                        to="dclinic.business",
                    ),
                ),
            ],
            options={
                "unique_together": {("business", "day_of_week")},
            },
        ),
    ]
