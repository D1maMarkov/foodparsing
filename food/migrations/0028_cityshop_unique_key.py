# Generated by Django 5.0 on 2024-11-08 15:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("food", "0027_remove_cityshop_unique_key_alter_cityshop_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="cityshop",
            name="unique_key",
            field=models.CharField(max_length=30, null=True, unique=True),
        ),
    ]
