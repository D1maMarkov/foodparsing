# Generated by Django 5.0 on 2024-12-09 19:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("food", "0039_alter_dish_unique_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shop",
            name="address",
            field=models.CharField(max_length=100, verbose_name="Адрес"),
        ),
        migrations.AlterField(
            model_name="shop",
            name="image",
            field=models.URLField(verbose_name="Изображение"),
        ),
    ]
