# Generated by Django 5.0.6 on 2024-09-03 12:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_serviceenquiry_is_viewed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceenquiry',
            name='is_viewed',
        ),
    ]
