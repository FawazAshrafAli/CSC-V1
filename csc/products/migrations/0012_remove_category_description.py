# Generated by Django 5.0.6 on 2024-08-28 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_productenquiry_is_viewed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='description',
        ),
    ]
