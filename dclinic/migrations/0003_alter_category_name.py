# Generated by Django 5.0.7 on 2024-08-04 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dclinic", "0002_category_service_professionals"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
