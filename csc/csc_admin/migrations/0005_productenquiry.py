# Generated by Django 5.0.6 on 2024-09-25 16:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_admin', '0004_serviceenquiry_location'),
        ('products', '0012_remove_category_description'),
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
                ('is_viewed', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True, max_length=150, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin_product_enquiry_product', to='products.product')),
            ],
            options={
                'db_table': 'admin_product_enquiry',
                'ordering': ['-created'],
            },
        ),
    ]
