# Generated by Django 5.0.6 on 2024-08-30 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact_us', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='enquiry',
            name='is_viewed',
            field=models.BooleanField(default=False),
        ),
    ]
