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
    siteId = tables.Column(verbose_name="Akamai Site ID")
    cacheMemoryProfileId = tables.LinkColumn(verbose_name="Cache Memory Profile")

    class Meta(BaseTable.Meta):
        model = models.CdnSite
        fields = (
            'pk',
            'name',
            'status',
            'cdn_site_role',
            'region',
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
            'region',
            'site',
            'bandwidthLimitMbps',
            'cacheMemoryProfileId',
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


# class CdnConfigContextSchemaTable(BaseTable):
#     pk = ToggleColumn()
#     name = tables.LinkColumn()
#     owner = tables.LinkColumn()
#     actions = ButtonsColumn(models.CdnConfigContextSchema, pk_field="slug")

#     class Meta(BaseTable.Meta):
#         model = models.CdnConfigContextSchema
#         fields = (
#             "pk",
#             "name",
#             "owner",
#             "description",
#             "actions",
#         )
#         default_columns = ("pk", "name", "description", "actions")


# class CdnConfigContextSchemaValidationStateColumn(tables.Column):
#     """
#     Custom column that validates an instance's context data against a config context schema
#     """

#     def __init__(self, validator, data_field, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.validator = validator
#         self.data_field = data_field

#     def render(self, record):
#         data = getattr(record, self.data_field)
#         try:
#             self.validator.validate(data)
#         except JSONSchemaValidationError as e:
#             # Return a red x (like a boolean column) and the validation error message
#             return render_boolean(False) + format_html('<span class="text-danger">{}</span>', e.message)

#         # Return a green check (like a boolean column)
#         return render_boolean(True)