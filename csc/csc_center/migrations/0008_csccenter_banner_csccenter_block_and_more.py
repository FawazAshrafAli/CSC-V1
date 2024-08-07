# Generated by Django 5.0.6 on 2024-07-10 15:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0007_socialmedialink'),
        ('products', '0001_initial'),
        ('services', '0002_alter_service_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='csccenter',
            name='banner',
            field=models.ImageField(default=None, upload_to='csc_center_banners/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='block',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='csc_center.block'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='contact_number',
            field=models.CharField(default=None, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='description',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='district',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='csc_center.district'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='email',
            field=models.EmailField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='fri_closing_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='fri_opening_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='keywords',
            field=models.ManyToManyField(to='csc_center.csckeywords'),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='landmark_or_building_name',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='location',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='location_latitude',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='location_longitude',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='logo',
            field=models.ImageField(default=None, upload_to='csc_center_logos/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='mobile_number',
            field=models.CharField(default=None, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='mon_closing_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='mon_opening_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='name',
            field=models.CharField(default=None, max_length=150, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='products',
            field=models.ManyToManyField(to='products.product'),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='sat_closing_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='sat_opening_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='services',
            field=models.ManyToManyField(to='services.service'),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='social_media_links',
            field=models.ManyToManyField(to='csc_center.socialmedialink'),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='state',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='csc_center.state'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='street',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='sun_closing_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='sun_opening_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='thu_closing_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='thu_opening_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='tue_closing_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='tue_opening_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='type',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='csc_center.csccentertype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='website',
            field=models.URLField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='wed_closing_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='wed_opening_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='csccenter',
            name='whatsapp_number',
            field=models.CharField(default=None, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csccenter',
            name='zipcode',
            field=models.CharField(default=None, max_length=15),
            preserve_default=False,
        ),
    ]
