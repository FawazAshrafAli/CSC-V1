# Generated by Django 5.0.6 on 2024-08-17 14:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0031_csccenter_owner'),
        ('posters', '0003_alter_poster_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomPoster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('poster', models.ImageField(upload_to='custom_posters/')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('csc_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csc_center.csccenter')),
            ],
        ),
    ]