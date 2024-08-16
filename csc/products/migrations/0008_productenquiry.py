# Generated by Django 5.0.6 on 2024-08-07 14:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0030_rename_show_working_time_csccenter_show_opening_hours'),
        ('products', '0007_rename_stock_product_quantity'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductEnquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applicant_name', models.CharField(max_length=150)),
                ('applicant_email', models.EmailField(max_length=254)),
                ('applicant_phone', models.CharField(max_length=20)),
                ('message', models.TextField()),
                ('slug', models.SlugField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('csc_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csc_center.csccenter')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
            options={
                'db_table': 'product_enquiry',
                'ordering': ['-created'],
            },
        ),
    ]