# Generated by Django 5.0.6 on 2024-07-17 12:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0014_keywords'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Keywords',
            new_name='CscKeywords',
        ),
    ]
