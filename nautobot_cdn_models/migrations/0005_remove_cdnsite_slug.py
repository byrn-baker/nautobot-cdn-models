# Generated by Django 3.2.20 on 2023-08-07 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nautobot_cdn_models', '0004_alter_cdnsite_neighbor2_preference'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cdnsite',
            name='slug',
        ),
    ]