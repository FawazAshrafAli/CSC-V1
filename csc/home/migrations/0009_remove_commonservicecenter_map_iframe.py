# Generated by Django 5.0.6 on 2024-05-28 10:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_commonservicecenter_map_iframe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commonservicecenter',
            name='map_iframe',
        ),
    ]
