# Generated by Django 4.2 on 2024-08-23 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0008_dish_image_restoraunt_owner_restoraunt_schedule_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DishCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Категория блюд')),
            ],
        ),
    ]