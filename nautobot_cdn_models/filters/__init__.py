import django_filters

from nautobot.core.filters import (
    NameSearchFilterSet,
    NaturalKeyOrPKMultipleChoiceFilter,
    RelatedMembershipBooleanFilter,
    SearchFilter,
    TreeNodeMultipleChoiceFilter,
)
from nautobot.core.utils.deprecation import class_deprecated_in_favor_of
from nautobot.extras.filters import NautobotFilterSet
from nautobot.dcim.models import Device, Location
from nautobot.ipam.models import IPAddress, Prefix
from nautobot.virtualization.models import VirtualMachine
from ..filters.mixins import CdnSiteModelFilterSetMixin
from ..models import CdnSite, SiteRole


__all__ = (
    "CdnsiteFilterSet",
    "CdnsiteModelFilterSetMixin",
    "CdnsiteFilterSet",
    "SiteRoleFilterSet",
)


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
    site_role = TreeNodeMultipleChoiceFilter(
        queryset=SiteRole.objects.all(),
        field_name="site_role",
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
            "comments",
            "description",
            "id",
            "name",
            "tags",
        ]


# TODO: remove in 2.2
@class_deprecated_in_favor_of(CdnsiteModelFilterSetMixin)
class CdnsiteFilterSet(CdnsiteModelFilterSetMixin):
    pass