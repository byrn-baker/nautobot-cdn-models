# Generated by Django 3.2.23 on 2023-11-25 16:54

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nautobot_cdn_models', '0016_auto_20231122_1710'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cdnsite',
            name='cacheMemoryProfileId',
        ),
        migrations.AddField(
            model_name='cdnsite',
            name='hyperCacheMemoryProfileId',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='hyperCacheMemoryProfileId', to='nautobot_cdn_models.hypercachememoryprofile'),
        ),
        migrations.AlterField(
            model_name='origin',
            name='ipAddressTypes',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=4), size=6), blank=True, null=True, size=6),
        ),
        migrations.AlterField(
            model_name='origin',
            name='resolvableHostnames',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=10), size=10), blank=True, null=True, size=10),
        ),
    ]
