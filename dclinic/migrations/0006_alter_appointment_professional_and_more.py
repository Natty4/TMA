# Generated by Django 5.0.7 on 2024-10-20 12:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dclinic", "0005_auser_passport_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="professional",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="appointments",
                to="dclinic.professional",
            ),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="service",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="appointments",
                to="dclinic.service",
            ),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="appointments",
                to="dclinic.auser",
            ),
        ),
    ]