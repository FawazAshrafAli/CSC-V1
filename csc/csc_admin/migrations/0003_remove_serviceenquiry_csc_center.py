# Generated by Django 5.0.6 on 2024-09-25 11:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('csc_admin', '0002_serviceenquiry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceenquiry',
            name='csc_center',
        ),
    ]