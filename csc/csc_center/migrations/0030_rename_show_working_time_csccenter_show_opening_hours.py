# Generated by Django 5.0.6 on 2024-07-26 16:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0029_csccenter_show_social_media_links_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='csccenter',
            old_name='show_working_time',
            new_name='show_opening_hours',
        ),
    ]
