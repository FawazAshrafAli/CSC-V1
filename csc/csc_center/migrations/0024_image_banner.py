# Generated by Django 5.0.6 on 2024-07-23 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0023_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='banner',
            field=models.ImageField(default=None, upload_to='rough_banner/'),
            preserve_default=False,
        ),
    ]