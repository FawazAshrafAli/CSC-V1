# Generated by Django 5.0.6 on 2024-07-17 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0015_rename_keywords_csckeywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='csccenter',
            name='keywords',
            field=models.ManyToManyField(to='csc_center.csckeywords'),
        ),
    ]
