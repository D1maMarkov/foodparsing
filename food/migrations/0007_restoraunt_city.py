# Generated by Django 4.2 on 2024-08-23 14:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0006_restoraunt_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='restoraunt',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='food.city', verbose_name='Город'),
        ),
    ]
