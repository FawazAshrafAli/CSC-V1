# Generated by Django 5.0.6 on 2024-05-28 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_commonservicecenter_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='commonservicecenter',
            name='map_iframe',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
