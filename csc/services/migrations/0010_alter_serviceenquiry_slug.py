# Generated by Django 5.0.6 on 2024-09-09 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_remove_serviceenquiry_is_viewed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceenquiry',
            name='slug',
            field=models.SlugField(blank=True, max_length=150, null=True),
        ),
    ]