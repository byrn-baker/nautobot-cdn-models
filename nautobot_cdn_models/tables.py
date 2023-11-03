import django_tables2 as tables

from nautobot.core.tables import (
    BaseTable,
    ButtonsColumn,
    LinkedCountColumn,
    TagColumn,
    ToggleColumn,
)
from nautobot.extras.tables import StatusTableMixin
from .models import CdnSite, SiteRole, HyperCacheMemoryProfile

TREE_LINK = """
{% load helpers %}
{% for i in record.tree_depth|as_range %}
    <i class="mdi mdi-circle-small"></i>
{% endfor %}
<a href="{{ record.get_absolute_url }}">{{ record.name }}</a>
"""


#
# Table columns
#


class CdnSiteColumn(tables.TemplateColumn):
    """
    Column for linking to a record's associated CDN Site.
    """

    template_code = """
    {% if record.cdnsite %}
        <a href="{{ record.cdnsite.get_absolute_url }}" title="{{ record.cdnsite.name }}">{{ record.cdnsite }}</a>
    {% else %}
        &mdash;
    {% endif %}
    """

    def __init__(self, *args, **kwargs):
        super().__init__(template_code=self.template_code, *args, **kwargs)

    def value(self, **kwargs):
        return str(kwargs["value"]) if kwargs["value"] else None

class HyperCacheMemoryProfileTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name="Site HyperCache Memory Profile Name")

    class Meta(BaseTable.Meta):
        model = HyperCacheMemoryProfile
        fields = (
            'pk',
            'name',
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
            'description',
            'hotCacheMemoryPercent',
            'ramOnlyCacheMemoryPercent',
            'diskIndexMemoryPercent',
            'frontEndCacheMemoryPercent',
            'cacheMemoryProfileId',
        )

#
# Site Roles
#


class SiteRoleTable(BaseTable):
    pk = ToggleColumn()
    name = tables.TemplateColumn(template_code=TREE_LINK, orderable=False, attrs={"td": {"class": "text-nowrap"}})
    cdnsite_count = LinkedCountColumn(
        viewname="cdnsite:cdnsite_list",
        url_params={"cdn_site_role": "name"},
        verbose_name="CdnSites",
    )
    actions = ButtonsColumn(SiteRole)

    class Meta(BaseTable.Meta):
        model = SiteRole
        fields = ("pk", "name", "cdnsite_count", "description", "actions")
        default_columns = ("pk", "name", "cdnsite_count", "description", "actions")


#
# CdnSites
#


class CdnSiteTable(StatusTableMixin, BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name="Akamai Site Name")
    cdn_site_role = tables.LinkColumn()
    location = tables.LinkColumn()
    bandwidthLimitMbps = tables.Column(verbose_name="Site Bandwidth Limit (MB)")
    enableDisklessMode = tables.Column(verbose_name="Enable Diskless Mode")
    neighbor1 = tables.LinkColumn(verbose_name="Primary Site Neighbor")
    neighbor1_preference = tables.Column(verbose_name="Primary Site Neighbor Preference")
    neighbor2 = tables.LinkColumn(verbose_name="Secondary Site Neighbor")
    neighbor2_preference = tables.Column(verbose_name="Secondary Site Neighbor Preference")
    siteId = tables.Column(verbose_name="Akamai Site ID")
    cacheMemoryProfileId = tables.LinkColumn(verbose_name="Cache Memory Profile")

    class Meta(BaseTable.Meta):
        model = CdnSite
        fields = (
            'pk',
            'name',
            'status',
            'cdn_site_role',
            'location',
            'abbreviatedName',
            'bandwidthLimitMbps',
            'enableDisklessMode',
            'neighbor1',
            'neighbor1_preference',
            'neighbor2',
            'neighbor2_preference',
            'cacheMemoryProfileId',
            'siteId',
        )
        default_columns = (
            'pk',
            'name',
            'status',
            'cdn_site_role',
            'location',
            'bandwidthLimitMbps',
            'cacheMemoryProfileId',
            'siteId',
        )
    
    def render_cacheMemoryProfileId(self, record):
        related_cacheMemoryProfileId = record.cacheMemoryProfileId
        if related_cacheMemoryProfileId:
            return related_cacheMemoryProfileId.name
        return 'No associated Profile'

