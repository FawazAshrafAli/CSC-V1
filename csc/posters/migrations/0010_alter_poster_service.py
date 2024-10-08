# Generated by Django 5.0.6 on 2024-09-10 11:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0009_poster_service'),
        ('services', '0010_alter_serviceenquiry_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poster',
            name='service',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='services.service'),
            preserve_default=False,
        ),
    ]
