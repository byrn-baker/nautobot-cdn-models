import django_filters
from django.db import models
import django_filters


from nautobot.extras.filters.mixins import (
    LocalContextModelFilterSetMixin,
    StatusModelFilterSetMixin,
)

from nautobot.extras.filters import (
    NautobotFilterSet,
    LocalContextModelFilterSetMixin,
    StatusModelFilterSetMixin,
)
from nautobot.utilities.filters import (
    BaseFilterSet,
    ContentTypeFilter,
    NaturalKeyOrPKMultipleChoiceFilter,
    SearchFilter,
    TreeNodeMultipleChoiceFilter,
)
from nautobot.extras.models import ConfigContextSchema
from nautobot.dcim.models import Region, Site
from . import models

class HyperCacheMemoryProfileFilterSet(NautobotFilterSet):
    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
        },
    )
    class Meta:
        model = models.HyperCacheMemoryProfile
        fields = "__all__"

class SiteRoleFilterSet(NautobotFilterSet):
    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
        },
    )
    class Meta:
        model = models.SiteRole
        fields = "__all__"

class CdnSiteFilterSet(NautobotFilterSet, LocalContextModelFilterSetMixin, StatusModelFilterSetMixin,):
    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
        },
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name="region",
        label="Region (ID)",
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name="region",
        label="Region (slug)",
    )
    site_id = TreeNodeMultipleChoiceFilter(
        queryset=Site.objects.all(),
        field_name="site",
        label="Site (ID)",
    )
    site = TreeNodeMultipleChoiceFilter(
        queryset=Site.objects.all(),
        field_name="site",
        label="Site (slug)",
    )
    cdn_site_role = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=models.SiteRole.objects.all(),
        label="Site Role (slug or ID)"
    )
    hyperCacheMemoryProfileId = django_filters.ModelChoiceFilter(
        field_name='name',
        to_field_name='name',
        queryset=models.HyperCacheMemoryProfile.objects.all(),
    )
    class Meta:
        model = models.CdnSite
        fields = [
        "name",
        "abbreviatedName",
        "bandwidthLimitMbps",
        "enableDisklessMode",
        "siteId",
        "cdn_site_role",
        "region",
        "site",
        "hyperCacheMemoryProfileId",
        "neighbor1",
        "neighbor1_preference",
        "neighbor2",
        "neighbor2_preference",
        'failover_site',
    ]

#
# Config Contexts
#


class CdnConfigContextFilterSet(BaseFilterSet):
    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "description": "icontains",
            "data": "icontains",
        },
    )
    owner_content_type = ContentTypeFilter()
    schema = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="schema",
        queryset=ConfigContextSchema.objects.all(),
        to_field_name="slug",
        label="Schema (slug or PK)",
    )
    region_id = django_filters.ModelMultipleChoiceFilter(
        field_name="regions",
        queryset=Region.objects.all(),
        label="Region (ID) - Deprecated (use region filter)",
    )
    region = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="regions",
        queryset=Region.objects.all(),
        label="Region (ID or slug)",
    )
    cdnsite_id = django_filters.ModelMultipleChoiceFilter(
        field_name="cdnsites",
        queryset=models.CdnSite.objects.all(),
        label="Site (ID) - Deprecated (use site filter)",
    )
    cdnsite = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="cdnsites",
        queryset=models.CdnSite.objects.all(),
        label="Site (ID or slug)",
    )
    # cdn_site_role_id = django_filters.ModelMultipleChoiceFilter(
    #     field_name="siteroles",
    #     queryset=models.SiteRole.objects.all(),
    #     label="Role (ID) - Deprecated (use role filter)",
    # )
    cdn_site_role = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="siteroles",
        queryset=models.SiteRole.objects.all(),
        label="Role (ID or slug)",
    )

    # Conditional enablement of dynamic groups filtering
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    class Meta:
        model = models.CdnConfigContext
        fields = ["id", "name", "is_active", "owner_content_type", "owner_object_id"]


#
# Content Delivery
#

class ServiceProviderFilterSet(NautobotFilterSet):
    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
        },
    )
    class Meta:
        model = models.ServiceProvider
        fields = "__all__"

class ContentProviderFilterSet(NautobotFilterSet):
    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
        },
    )
    class Meta:
        model = models.ContentProvider
        fields = "__all__"

class OriginFilterSet(NautobotFilterSet):
    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
        },
    )
    class Meta:
        model = models.Origin
        fields = [
            'name',
            'contentProviderId',
            'enable',
            'originTimeout',
        ]