# Generated by Django 3.2.20 on 2023-08-22 16:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nautobot_cdn_models', '0005_remove_cdnsite_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cdnsite',
            name='failover_site',
        ),
    ]
