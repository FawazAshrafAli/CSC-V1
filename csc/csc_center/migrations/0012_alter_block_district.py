# Generated by Django 5.0.6 on 2024-07-11 12:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0011_alter_block_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='district',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csc_center.district'),
        ),
    ]
