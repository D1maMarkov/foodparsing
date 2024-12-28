# Generated by Django 5.0 on 2024-10-31 16:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("food", "0020_restorauntref_remove_restorauntdish_dish_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="city",
            options={"verbose_name": "Город", "verbose_name_plural": "Города"},
        ),
        migrations.AlterModelOptions(
            name="dish",
            options={"verbose_name": "Блюдо", "verbose_name_plural": "Блюда"},
        ),
        migrations.AlterModelOptions(
            name="dishcategory",
            options={"verbose_name": "Категория блюда", "verbose_name_plural": "Категории блюд"},
        ),
        migrations.AlterModelOptions(
            name="food",
            options={"verbose_name": "Кухня", "verbose_name_plural": "Кухни"},
        ),
        migrations.AlterModelOptions(
            name="restoraunt",
            options={"verbose_name": "Ресторан", "verbose_name_plural": "Рестораны"},
        ),
        migrations.AddField(
            model_name="dish",
            name="unique_key",
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]