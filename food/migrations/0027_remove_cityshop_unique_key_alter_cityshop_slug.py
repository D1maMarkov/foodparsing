# Generated by Django 5.0 on 2024-11-08 15:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("food", "0026_shop_alter_dish_slug_alter_restoraunt_unique_key_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cityshop",
            name="unique_key",
        ),
        migrations.AlterField(
            model_name="cityshop",
            name="slug",
            field=models.CharField(max_length=90),
        ),
    ]
