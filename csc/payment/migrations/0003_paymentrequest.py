# Generated by Django 5.0.6 on 2024-09-17 16:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0039_rename_csc_center_id_banner_csc_center'),
        ('payment', '0002_remove_paymenthistory_currency'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_token', models.CharField(max_length=225, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(default='pending', max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('csc_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csc_center.csccenter')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]
