# Generated by Django 5.0.6 on 2024-09-10 16:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0039_rename_csc_center_id_banner_csc_center'),
        ('posters', '0011_remove_poster_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customposter',
            name='description',
        ),
        migrations.AddField(
            model_name='customposter',
            name='state',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='csc_center.state'),
            preserve_default=False,
        ),
    ]
