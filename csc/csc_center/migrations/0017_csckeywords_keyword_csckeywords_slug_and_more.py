# Generated by Django 5.0.6 on 2024-07-17 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0016_csccenter_keywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='csckeywords',
            name='keyword',
            field=models.CharField(default=None, max_length=150, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='csckeywords',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
        migrations.AlterModelTable(
            name='csckeywords',
            table='csc_keywords',
        ),
    ]
