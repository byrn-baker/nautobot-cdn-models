# Generated by Django 3.2.20 on 2023-07-14 14:44

import django.core.serializers.json
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import nautobot.core.fields
import nautobot.extras.models.mixins
import nautobot.extras.models.models
import nautobot.extras.models.statuses
import nautobot.extras.utils
import nautobot.utilities.fields
import nautobot.utilities.ordering
import taggit.managers
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0019_device_redundancy_group_data_migration'),
        ('extras', '0053_relationship_required_on'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteRole',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('_custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', nautobot.core.fields.AutoSlugField(blank=True, max_length=100, populate_from='name', unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='nautobot_cdn_models.siterole')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model, nautobot.extras.models.mixins.DynamicGroupMixin, nautobot.extras.models.mixins.NotesMixin),
        ),
        migrations.CreateModel(
            name='HyperCacheMemoryProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('_custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('name', models.CharField(max_length=255)),
                ('slug', nautobot.core.fields.AutoSlugField(blank=True, max_length=100, populate_from='name', unique=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('frontEndCacheMemoryPercent', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('ramOnlyCacheMemoryPercent', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('hotCacheMemoryPercent', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('diskIndexMemoryPercent', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('cacheMemoryProfileId', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10000)])),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
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
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('_custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('local_context_data', models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True)),
                ('local_context_data_owner_object_id', models.UUIDField(blank=True, default=None, null=True)),
                ('name', models.CharField(max_length=255)),
                ('_name', nautobot.utilities.fields.NaturalOrderingField('name', blank=True, db_index=True, max_length=100, naturalize_function=nautobot.utilities.ordering.naturalize)),
                ('slug', nautobot.core.fields.AutoSlugField(blank=True, max_length=100, populate_from='name', unique=True)),
                ('abbreviatedName', models.CharField(blank=True, max_length=255)),
                ('bandwidthLimitMbps', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1000), django.core.validators.MaxValueValidator(10000000)])),
                ('enableDisklessMode', models.BooleanField(default=False)),
                ('neighbor1_preference', models.IntegerField(blank=True, default=1000, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10000)])),
                ('neighbor2_preference', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10000)])),
                ('siteId', models.IntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10000)])),
                ('cacheMemoryProfileId', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='CacheMemoryProfileId', to='nautobot_cdn_models.hypercachememoryprofile')),
                ('cdn_site_role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cdnsites', to='nautobot_cdn_models.siterole')),
                ('failover_site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='failover', to='nautobot_cdn_models.cdnsite')),
                ('local_context_data_owner_content_type', models.ForeignKey(blank=True, default=None, limit_choices_to=nautobot.extras.utils.FeatureQuery('config_context_owners'), null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('local_context_schema', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='extras.configcontextschema')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cdnsites', to='dcim.location')),
                ('neighbor1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_neighbor', to='nautobot_cdn_models.cdnsite')),
                ('neighbor2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='secondary_neighbor', to='nautobot_cdn_models.cdnsite')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cdnsites', to='dcim.region')),
                ('status', nautobot.extras.models.statuses.StatusField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='nautobot_cdn_models_cdnsite_related', to='extras.status')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ['cdn_site_role', '_name'],
                'unique_together': {('cdn_site_role', 'region', 'name')},
            },
            bases=(models.Model, nautobot.extras.models.mixins.DynamicGroupMixin, nautobot.extras.models.mixins.NotesMixin, nautobot.extras.models.models.ConfigContextSchemaValidationMixin),
        ),
    ]
