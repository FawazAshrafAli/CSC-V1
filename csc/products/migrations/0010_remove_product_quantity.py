# Generated by Django 5.0.6 on 2024-08-12 16:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_alter_productenquiry_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='quantity',
        ),
    ]