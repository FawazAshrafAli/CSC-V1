# Generated by Django 5.0.6 on 2024-08-12 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0030_rename_show_working_time_csccenter_show_opening_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='csccenter',
            name='owner',
            field=models.CharField(default='John', max_length=150),
            preserve_default=False,
        ),
    ]
