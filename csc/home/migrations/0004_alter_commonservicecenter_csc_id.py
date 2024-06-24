# Generated by Django 5.0.6 on 2024-05-27 06:41

import home.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_service_commonservicecenter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commonservicecenter',
            name='csc_id',
            field=models.CharField(default=home.models.generate_csc_id, max_length=50, primary_key=True, serialize=False),
        ),
    ]
