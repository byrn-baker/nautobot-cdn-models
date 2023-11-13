import django_tables2 as tables
from django.conf import settings
from django.utils.html import format_html
from jsonschema.exceptions import ValidationError as JSONSchemaValidationError

from nautobot.core.templatetags.helpers import render_boolean, render_markdown
from nautobot.core.tables import (
    BaseTable,
    ButtonsColumn,
    BooleanColumn,
    LinkedCountColumn,
    TagColumn,
    ToggleColumn,
)
from nautobot.extras.tables import StatusTableMixin
from .models import CdnSite, SiteRole, HyperCacheMemoryProfile, RedirectMapContext

TREE_LINK = """
{% load helpers %}
{% for i in record.tree_depth|as_range %}
    <i class="mdi mdi-circle-small"></i>
{% endfor %}
<a href="{{ record.get_absolute_url }}">{{ record.name }}</a>
"""

CDNGITREPOSITORY_PROVIDES = """
<span class="text-nowrap">
{% for entry in datasource_contents %}
<span style="display: inline-block" title="{{ entry.name|title }}"
class="label label-{% if entry.content_identifier in record.provided_contents %}success{% else %}default{% endif %}">
<i class="mdi {{ entry.icon }}"></i></span>
{% endfor %}
</span>
"""

CDNGITREPOSITORY_BUTTONS = """
<button data-url="{% url 'nautobot_cdn_models:cdngitrepository_sync' pk=record.pk %}" type="submit" class="btn btn-primary btn-xs sync-repository" title="Sync" {% if not perms.nautobot_cdn_models.change_cdngitrepository %}disabled="disabled"{% endif %}><i class="mdi mdi-source-branch-sync" aria-hidden="true"></i></button>
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
        viewname="plugins:nautobot_cdn_models:cdnsite_list",
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

CDNSITE_LINK = """
<a href="{% url '"plugins:nautobot_cdn_models:cdnsite' pk=record.pk %}">
    {{ record.name|default:'<span class="label label-info">Unnamed site</span>' }}
</a>
"""

class CdnSiteImportTable(BaseTable):
    name = tables.Column(verbose_name="Akamai Site Name")
    cdn_site_role = tables.Column(verbose_name="Site Role")
    location = tables.Column(verbose_name="Location")
    abbreviatedName = tables.Column(verbose_name="Abbreviated Name")
    bandwidthLimitMbps = tables.Column(verbose_name="Bandwidth Limit (MB)")
    enableDisklessMode = tables.Column(verbose_name="Enable Diskless Mode")
    neighbor1 = tables.Column(verbose_name="Primary Site Neighbor")
    neighbor1_preference = tables.Column(verbose_name="Primary Site Neighbor Preference")
    neighbor2 = tables.Column(verbose_name="Secondary Site Neighbor")
    neighbor2_preference = tables.Column(verbose_name="Secondary Site Neighbor Preference")
    siteId = tables.Column(verbose_name="Akamai Site ID")
    cacheMemoryProfileId = tables.Column(verbose_name="Cache Memory Profile")

    class Meta(BaseTable.Meta):
        model = CdnSite
        fields = (
            'name',
            'status',
            'cdn_site_role',
            'location',
            'abbreviatedName',
            'bandwidthLimitMbps',
            'enableDisklessMode',
            'siteId',
        )
        empty_text = False

class RedirectMapContextTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    owner = tables.LinkColumn()
    is_active = BooleanColumn(verbose_name="Active")

    class Meta(BaseTable.Meta):
        model = RedirectMapContext
        fields = (
            "pk",
            "name",
            "owner",
            "weight",
            "is_active",
            "description",
            "locations",
            "cdnsites",
            "cdn_site_roles",
        )
        default_columns = ("pk", "name", "weight", "is_active", "description")
        