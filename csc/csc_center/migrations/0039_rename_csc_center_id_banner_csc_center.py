# Generated by Django 5.0.6 on 2024-09-09 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0038_remove_csccenter_banner_csccenter_banners'),
    ]

    operations = [
        migrations.RenameField(
            model_name='banner',
            old_name='csc_center_id',
            new_name='csc_center',
        ),
    ]
