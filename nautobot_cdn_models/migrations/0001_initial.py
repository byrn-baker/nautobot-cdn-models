# Generated by Django 3.2.22 on 2023-11-03 16:04

import django.core.serializers.json
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import nautobot.core.models.fields
import nautobot.core.models.tree_queries
import nautobot.extras.models.mixins
import nautobot.extras.models.statuses
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0098_rename_data_jobresult_result'),
        ('dcim', '0049_remove_slugs_and_change_device_primary_ip_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteRole',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('_custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='nautobot_cdn_models.siterole')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model, nautobot.extras.models.mixins.DynamicGroupMixin, nautobot.extras.models.mixins.NotesMixin),
            managers=[
                ('objects', nautobot.core.models.tree_queries.TreeManager()),
            ],
        ),
        migrations.CreateModel(
            name='HyperCacheMemoryProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('_custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('frontEndCacheMemoryPercent', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('ramOnlyCacheMemoryPercent', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('hotCacheMemoryPercent', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('diskIndexMemoryPercent', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('cacheMemoryProfileId', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10000)])),
                ('tags', nautobot.core.models.fields.TagsField(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, nautobot.extras.models.mixins.DynamicGroupMixin, nautobot.extras.models.mixins.NotesMixin),
        ),
        migrations.CreateModel(
            name='CdnSite',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('_custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('name', models.CharField(max_length=100)),
                ('abbreviatedName', models.CharField(blank=True, max_length=255)),
                ('bandwidthLimitMbps', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1000), django.core.validators.MaxValueValidator(10000000)])),
                ('enableDisklessMode', models.BooleanField(default=False)),
                ('neighbor1_preference', models.IntegerField(blank=True, default=1000, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10000)])),
                ('neighbor2_preference', models.IntegerField(blank=True, default=750, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10000)])),
                ('siteId', models.IntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10000)])),
                ('cacheMemoryProfileId', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='CacheMemoryProfileId', to='nautobot_cdn_models.hypercachememoryprofile')),
                ('cdn_site_role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cdnsites', to='nautobot_cdn_models.siterole')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cdnsites', to='dcim.location')),
                ('neighbor1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_neighbor', to='nautobot_cdn_models.cdnsite')),
                ('neighbor2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='secondary_neighbor', to='nautobot_cdn_models.cdnsite')),
                ('status', nautobot.extras.models.statuses.StatusField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cdn_sites', to='extras.status')),
                ('tags', nautobot.core.models.fields.TagsField(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ['cdn_site_role', 'name'],
                'unique_together': {('cdn_site_role', 'location', 'name')},
            },
            bases=(models.Model, nautobot.extras.models.mixins.DynamicGroupMixin, nautobot.extras.models.mixins.NotesMixin),
        ),
    ]
