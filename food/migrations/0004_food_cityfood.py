# Generated by Django 4.2 on 2024-08-23 12:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0003_city_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='кухня')),
                ('slug', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CityFood',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='food.city', verbose_name='город')),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='food.food', verbose_name='кухня')),
            ],
        ),
    ]
