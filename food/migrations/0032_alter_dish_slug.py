# Generated by Django 5.0 on 2024-11-21 15:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("food", "0031_alter_dishref_dish_alter_restoraunt_unique_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dish",
            name="slug",
            field=models.CharField(max_length=80),
        ),
    ]