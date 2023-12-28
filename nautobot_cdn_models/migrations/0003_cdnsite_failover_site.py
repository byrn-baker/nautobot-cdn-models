# Generated by Django 3.2.22 on 2023-11-11 20:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nautobot_cdn_models', '0002_delete_cdngitrepository'),
    ]

    operations = [
        migrations.AddField(
            model_name='cdnsite',
            name='failover_site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sister_site', to='nautobot_cdn_models.cdnsite'),
        ),
    ]