# Generated by Django 5.0 on 2024-12-28 16:15

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("food", "0046_seo_text_alter_seo_page_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="seo",
            name="text",
            field=ckeditor.fields.RichTextField(blank=True, max_length=7000, null=True),
        ),
    ]