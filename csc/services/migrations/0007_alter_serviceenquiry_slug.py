# Generated by Django 5.0.6 on 2024-08-19 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_serviceenquiry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceenquiry',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]
