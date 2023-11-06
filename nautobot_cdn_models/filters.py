import django_filters

from nautobot.core.filters import (
    BaseFilterSet,
    ContentTypeFilter,
    NameSearchFilterSet,
    NaturalKeyOrPKMultipleChoiceFilter,
    RelatedMembershipBooleanFilter,
    SearchFilter,
    TreeNodeMultipleChoiceFilter,
)
from nautobot.extras.filters import NautobotFilterSet
from nautobot.dcim.models import Device, Location
from nautobot.ipam.models import IPAddress, Prefix
from nautobot.virtualization.models import VirtualMachine
from nautobot.extras.filters.mixins import (
    LocalContextModelFilterSetMixin,
    StatusModelFilterSetMixin,
)
from nautobot.extras.models import ConfigContextSchema
from .models import CdnSite, SiteRole, HyperCacheMemoryProfile, RedirectMapContext


__all__ = (
    "CdnSiteFilterSet",
    "SiteRoleFilterSet",
    "HyperCacheMemoryProfileFilterSet"
)

class HyperCacheMemoryProfileFilterSet(NautobotFilterSet):
    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
        },
    )
    class Meta:
        model = HyperCacheMemoryProfile
        fields = "__all__"
        
class SiteRoleFilterSet(NautobotFilterSet, NameSearchFilterSet):
    parent = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=SiteRole.objects.all(),
        label="Parent site role (name or ID)",
        to_field_name="name",
    )
    children = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=SiteRole.objects.all(),
        label="Children (name or ID)",
        to_field_name="name",
    )
    has_children = RelatedMembershipBooleanFilter(
        field_name="children",
        label="Has children",
    )
    cdnsits = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=CdnSite.objects.all(),
        label="CdnSites (name or ID)",
        to_field_name="name",
    )
    has_cdnsites = RelatedMembershipBooleanFilter(
        field_name="CdnSites",
        label="Has CdnSites",
    )

    class Meta:
        model = SiteRole
        fields = ["id", "name", "description"]


class CdnSiteFilterSet(NautobotFilterSet):
    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "description": "icontains",
            "comments": "icontains",
        },
    )
    cdn_site_role = TreeNodeMultipleChoiceFilter(
        queryset=SiteRole.objects.all(),
        field_name="cdn_site_role",
        label="Site Role (name or ID)",
        to_field_name="name",
    )
    devices = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Devices (name or ID)",
    )
    has_devices = RelatedMembershipBooleanFilter(
        field_name="devices",
        label="Has devices",
    )
    ip_addresses = django_filters.ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        label="IP addresses (ID)",
    )
    has_ip_addresses = RelatedMembershipBooleanFilter(
        field_name="ip_addresses",
        label="Has IP addresses",
    )
    locations = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        to_field_name="name",
        label="Locations (names and/or IDs)",
    )
    has_locations = RelatedMembershipBooleanFilter(
        field_name="locations",
        label="Has locations",
    )
    prefixes = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        label="Prefixes (ID)",
    )
    has_prefixes = RelatedMembershipBooleanFilter(
        field_name="prefixes",
        label="Has prefixes",
    )
    virtual_machines = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        to_field_name="name",
        label="Virtual machines (name or ID)",
    )
    has_virtual_machines = RelatedMembershipBooleanFilter(
        field_name="virtual_machines",
        label="Has virtual machines",
    )

    class Meta:
        model = CdnSite
        fields = [
            "id",
            "name",
        ]

#
# Config Contexts
#


class RedirectMapContextFilterSet(BaseFilterSet):
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
    location_id = django_filters.ModelMultipleChoiceFilter(
        field_name="locations",
        queryset=Location.objects.all(),
        label="Location (ID) - Deprecated (use region filter)",
    )
    region = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="Locations",
        queryset=Location.objects.all(),
        label="Location (ID or slug)",
    )
    cdnsite_id = django_filters.ModelMultipleChoiceFilter(
        field_name="cdnsites",
        queryset=CdnSite.objects.all(),
        label="Site (ID) - Deprecated (use site filter)",
    )
    cdnsite = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="cdnsites",
        queryset=CdnSite.objects.all(),
        label="Site (ID or slug)",
    )
    cdn_site_role_id = django_filters.ModelMultipleChoiceFilter(
        field_name="siteroles",
        queryset=SiteRole.objects.all(),
        label="Role (ID) - Deprecated (use role filter)",
    )
    cdn_site_role = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="siteroles",
        queryset=SiteRole.objects.all(),
        label="Role (ID or slug)",
    )

    # Conditional enablement of dynamic groups filtering
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    class Meta:
        model = RedirectMapContext
        fields = ["id", "name", "is_active", "owner_content_type", "owner_object_id"]