# Generated by Django 5.0 on 2024-10-31 14:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("food", "0019_food_genitive_case"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="restorauntdish",
            name="dish",
        ),
        migrations.RemoveField(
            model_name="restorauntdish",
            name="restoraunt",
        ),
        migrations.DeleteModel(
            name="RestorauntDish",
        ),
    ]