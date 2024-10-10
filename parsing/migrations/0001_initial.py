# Generated by Django 5.0 on 2024-10-08 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Proxy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=15)),
                ('port', models.CharField(max_length=10)),
                ('user', models.CharField(max_length=32)),
                ('password', models.CharField(max_length=32)),
            ],
            options={
                'verbose_name': 'Прокси',
                'verbose_name_plural': 'Прокси',
            },
        ),
    ]
