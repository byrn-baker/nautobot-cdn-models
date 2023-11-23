# Generated by Django 3.2.23 on 2023-11-22 16:24

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nautobot_cdn_models', '0013_auto_20231121_2153'),
    ]

    operations = [
        migrations.AddField(
            model_name='origin',
            name='cacheableErrorResponseCodes',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=10), size=10), default=list, size=10),
        ),
        migrations.AddField(
            model_name='origin',
            name='errorCacheMaxAge',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(60)]),
        ),
        migrations.AddField(
            model_name='origin',
            name='errorCacheMaxRetry',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(16)]),
        ),
        migrations.AlterField(
            model_name='origin',
            name='ipAddressTypes',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=4), size=2), size=2),
        ),
    ]