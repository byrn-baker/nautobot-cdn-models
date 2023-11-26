import django_tables2 as tables
from django.utils.html import format_html
from jsonschema.exceptions import ValidationError as JSONSchemaValidationError

from nautobot.utilities.tables import (
    BaseTable,
    BooleanColumn,
    ButtonsColumn,
    ToggleColumn,
    LinkedCountColumn
)
from nautobot.extras.tables import StatusTableMixin
from nautobot.utilities.templatetags.helpers import render_boolean

from . import models

class HyperCacheMemoryProfileTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name="Site HyperCache Memory Profile Name")
    slug= tables.Column(verbose_name="Slug")

    class Meta(BaseTable.Meta):
        model = models.HyperCacheMemoryProfile
        fields = (
            'pk',
            'name',
            'slug',
            'description',
            'hotCacheMemoryPercent',
            'ramOnlyCacheMemoryPercent',
            'diskIndexMemoryPercent',
            'frontEndCacheMemoryPercent',
            'cacheMemoryProfileId',

        )
        default_columns = (
            'pk',
            'name',
            'slug',
            'description',
            'hotCacheMemoryPercent',
            'ramOnlyCacheMemoryPercent',
            'diskIndexMemoryPercent',
            'frontEndCacheMemoryPercent',
            'cacheMemoryProfileId',
        )

MPTT_LINK = """
{% for i in record.get_ancestors %}
    <i class="mdi mdi-circle-small"></i>
{% endfor %}
<a href="{{ record.get_absolute_url }}">{{ record.name }}</a>
"""

class SiteRoleTable(BaseTable):
    pk = ToggleColumn()
    name = tables.TemplateColumn(template_code=MPTT_LINK, orderable=False, attrs={"td": {"class": "text-nowrap"}})
    slug= tables.Column(verbose_name="Slug")
    cdnsite_count = LinkedCountColumn(
        viewname="plugins:nautobot_cdn_models:cdnsite_list",
        url_params={"cdn_site_role": "slug"},
        verbose_name="CdnSites",
    )
    actions = ButtonsColumn(models.SiteRole, pk_field="slug")

    class Meta(BaseTable.Meta):
        model = models.SiteRole
        fields = ("pk", "name", "cdnsite_count", "description", "slug")
        default_columns = ("pk", "name", "cdnsite_count", "description")


class CdnSiteTable(StatusTableMixin, BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name="Akamai Site Name")
    cdn_site_role = tables.LinkColumn()
    region = tables.LinkColumn()
    site = tables.LinkColumn()
    bandwidthLimitMbps = tables.Column(verbose_name="Site Bandwidth Limit (MB)")
    enableDisklessMode = tables.Column(verbose_name="Enable Diskless Mode")
    neighbor1 = tables.LinkColumn(verbose_name="Primary Site Neighbor")
    neighbor1_preference = tables.Column(verbose_name="Primary Site Neighbor Preference")
    neighbor2 = tables.LinkColumn(verbose_name="Secondary Site Neighbor")
    neighbor2_preference = tables.Column(verbose_name="Secondary Site Neighbor Preference")
    failover_site =  tables.Column(verbose_name="Sister Site")
    siteId = tables.Column(verbose_name="Akamai Site ID")
    hyperCacheMemoryProfileId = tables.LinkColumn(verbose_name="Cache Memory Profile")

    class Meta(BaseTable.Meta):
        model = models.CdnSite
        fields = (
            'pk',
            'name',
            'status',
            'cdn_site_role',
            'region',
            'site',
            'abbreviatedName',
            'bandwidthLimitMbps',
            'enableDisklessMode',
            'neighbor1',
            'neighbor1_preference',
            'neighbor2',
            'neighbor2_preference',
            'failover_site',
            'hyperCacheMemoryProfileId',
            'siteId',
        )
        default_columns = (
            'pk',
            'name',
            'status',
            'cdn_site_role',
            'region',
            'bandwidthLimitMbps',
            'enableDisklessMode',
            'neighbor1',
            'neighbor2',
            'failover_site',
            'hyperCacheMemoryProfileId',
            'siteId',
        )
    
    def render_cacheMemoryProfileId(self, record):
        related_cacheMemoryProfileId = record.cacheMemoryProfileId
        if related_cacheMemoryProfileId:
            return related_cacheMemoryProfileId.name
        return 'No associated Profile'

class CdnConfigContextTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    owner = tables.LinkColumn()
    is_active = BooleanColumn(verbose_name="Active")

    class Meta(BaseTable.Meta):
        model = models.CdnConfigContext
        fields = (
            "pk",
            "name",
            "owner",
            "weight",
            "is_active",
            "description",
            "regions",
            "cdnsites",
            "cdn_site_roles",
        )
        default_columns = ("pk", "name", "weight", "is_active", "description")


#
# Content Delivery
#

class ServiceProviderTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    account = tables.Column()

    class Meta(BaseTable.Meta):
        model = models.ServiceProvider
        fields = (
            'pk',
            'name',
            'slug',
            'enable',
            'serviceProviderId',
        )
        default_columns = (
            'pk',
            'name',
            'slug',
            'enable',
            'serviceProviderId',
        )

class ContentProviderTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    serviceProviderId = tables.LinkColumn(verbose_name="Service Provider")

    class Meta(BaseTable.Meta):
        model = models.ContentProvider
        fields = (
            'pk',
            'name',
            'slug',
            'enable',
            'contentProviderId',
            'serviceProviderId',
        )
        default_columns = (
            'pk',
            'name',
            'slug',
            'enable',
            'contentProviderId',
            'serviceProviderId',
        )
    
    def render_serviceProviderId(self, record):
        related_serviceProviderId = record.serviceProviderId
        if related_serviceProviderId:
            return related_serviceProviderId.name
        return 'No associated Provider'

class OriginTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    contentProviderId = tables.LinkColumn(verbose_name="Content Provider")
    
    class Meta(BaseTable.Meta):
        model = models.Origin
        fields = (
            'pk',
            'name',
            'contentProviderId',
            'enable',
            'originTimeout',
        )
        default_columns = (
            'pk',
            'name',
            'contentProviderId',
            'enable',
            'originTimeout',
        )