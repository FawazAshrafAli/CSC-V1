# Generated by Django 5.0.6 on 2024-07-24 09:52

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0026_image_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='csccenter',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
