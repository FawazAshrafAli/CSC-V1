# Generated by Django 5.0.6 on 2024-07-10 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0003_csckeywords'),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=150)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]