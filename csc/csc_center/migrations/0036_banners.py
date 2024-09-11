# Generated by Django 5.0.6 on 2024-09-07 17:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0035_csccenter_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banners',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banner_image', models.ImageField(upload_to='csc_center_banners/')),
                ('csc_center_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csc_center.csccenter')),
            ],
        ),
    ]