# Generated by Django 5.0.6 on 2024-09-25 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_admin', '0003_remove_serviceenquiry_csc_center'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceenquiry',
            name='location',
            field=models.TextField(default='Melmuri, Malappuram, Malappuram Dist, kerala'),
            preserve_default=False,
        ),
    ]
