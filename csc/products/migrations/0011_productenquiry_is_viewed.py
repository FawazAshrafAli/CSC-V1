# Generated by Django 5.0.6 on 2024-08-24 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_remove_product_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='productenquiry',
            name='is_viewed',
            field=models.BooleanField(default=False),
        ),
    ]
