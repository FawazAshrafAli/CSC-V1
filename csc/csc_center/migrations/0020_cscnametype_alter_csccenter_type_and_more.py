# Generated by Django 5.0.6 on 2024-07-18 14:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0019_rename_csckeywords_csckeyword'),
    ]

    operations = [
        migrations.CreateModel(
            name='CscNameType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=150, unique=True)),
                ('slug', models.SlugField(blank=True, null=True)),
            ],
            options={
                'db_table': 'csc_name_type',
                'ordering': ['type'],
            },
        ),
        migrations.AlterField(
            model_name='csccenter',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csc_center.cscnametype'),
        ),
        migrations.DeleteModel(
            name='CscCenterType',
        ),
    ]
