# Generated by Django 4.2 on 2024-08-23 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0009_dishcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='dish',
            name='slug',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
