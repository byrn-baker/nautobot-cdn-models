# Generated by Django 3.2.23 on 2023-11-25 21:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nautobot_cdn_models', '0017_auto_20231125_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cdnsite',
            name='hyperCacheMemoryProfileId',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hyperCacheMemoryProfileId', to='nautobot_cdn_models.hypercachememoryprofile'),
        ),
    ]