# Generated by Django 5.0.6 on 2024-07-05 08:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_category_tag_alter_blog_options_blog_author_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blog',
            old_name='excerpt',
            new_name='summary',
        ),
    ]
