from django_tables2 import RequestConfig

from nautobot.core.views import mixins as view_mixins
from nautobot.circuits.models import Circuit
from nautobot.core.models.querysets import count_related
from nautobot.core.views import generic
from nautobot.core.views.paginator import EnhancedPaginator, get_paginate_count
from nautobot.dcim.models import Device, Location, Rack, RackReservation
from nautobot.ipam.models import IPAddress, Prefix, VLAN, VRF
from nautobot.virtualization.models import VirtualMachine, Cluster
from . import filters, forms, tables
from .models import CdnSite, HyperCacheMemoryProfile, SiteRole

class HyperCacheMemoryProfileUIViewSet(
    view_mixins.ObjectListViewMixin,
    view_mixins.ObjectDetailViewMixin,
    view_mixins.ObjectEditViewMixin,
    view_mixins.ObjectDestroyViewMixin,
    view_mixins.ObjectBulkDestroyViewMixin,
):
    queryset = HyperCacheMemoryProfile.objects.all()
    table_class = tables.HyperCacheMemoryProfileTable
    form_class = forms.HyperCacheMemoryProfileForm
    filterset_class = filters.HyperCacheMemoryProfileFilterSet
    filterset_form_class = forms.HyperCacheMemoryProfileFilterForm
    serializer_class = serializers.HyperCacheMemoryProfileSerializer
    action_buttons = ("add",)

## CDN Site Roles ##
class SiteRoleListView(generic.ObjectListView):
    queryset = SiteRole.objects.annotate(cdnsite_count=count_related(CdnSite, "site_role"))
    filterset = filters.SiteRoleFilterSet
    table = tables.SiteRoleTable


class SiteRoleView(generic.ObjectView):
    queryset = SiteRole.objects.all()

    def get_extra_context(self, request, instance):
        # CdnSite
        cndsites = CdnSite.objects.restrict(request.user, "view").filter(
            cdnsite_role__in=instance.descendants(include_self=True)
        )

        cdnsite_table = tables.CdnSiteTable(cdnsites)
        cdnsite_table.columns.hide("cdnsite_role")

        paginate = {
            "paginator_class": EnhancedPaginator,
            "per_page": get_paginate_count(request),
        }
        RequestConfig(request, paginate).configure(cdnsite_table)

        return {
            "cdnsite_table": cdnsite_table,
        }


class SiteRoleEditView(generic.ObjectEditView):
    queryset = SiteRole.objects.all()
    model_form = forms.SiteRoleForm


class SiteRoleDeleteView(generic.ObjectDeleteView):
    queryset = SiteRole.objects.all()


class SiteRoleBulkImportView(generic.BulkImportView):
    queryset = SiteRole.objects.all()
    table = tables.SiteRoleTable


class SiteRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = SiteRole.objects.annotate(cdnsite_count=count_related(CdnSite, "cdnsite_role"))
    table = tables.SiteRoleTable
    filterset = filters.SiteRoleFilterSet

## CDN SITES ##
class TenantListView(generic.ObjectListView):
    queryset = CdnSite.objects.select_related("cdnsite_role")
    filterset = filters.CdnSiteFilterSet
    filterset_form = forms.CdnSiteFilterForm
    table = tables.CdnSiteTable


class CdnSiteView(generic.ObjectView):
    queryset = CdnSite.objects.select_related("cdnsite_role")

    def get_extra_context(self, request, instance):
        stats = {
            # TODO: Should we include child locations of the filtered locations in the location_count below?
            "location_count": Location.objects.restrict(request.user, "view").filter(cdnsite=instance).count(),
            "rack_count": Rack.objects.restrict(request.user, "view").filter(cdnsite=instance).count(),
            "rackreservation_count": RackReservation.objects.restrict(request.user, "view")
            .filter(cdnsite=instance)
            .count(),
            "device_count": Device.objects.restrict(request.user, "view").filter(cdnsite=instance).count(),
            "vrf_count": VRF.objects.restrict(request.user, "view").filter(cdnsite=instance).count(),
            "prefix_count": Prefix.objects.restrict(request.user, "view").filter(cdnsite=instance).count(),
            "ipaddress_count": IPAddress.objects.restrict(request.user, "view").filter(cdnsite=instance).count(),
            "vlan_count": VLAN.objects.restrict(request.user, "view").filter(cdnsite=instance).count(),
            "circuit_count": Circuit.objects.restrict(request.user, "view").filter(cdnsite=instance).count(),
            "virtualmachine_count": VirtualMachine.objects.restrict(request.user, "view")
            .filter(cdnsite=instance)
            .count(),
            "cluster_count": Cluster.objects.restrict(request.user, "view").filter(cdnsite=instance).count(),
        }

        return {
            "stats": stats,
        }


class TenantEditView(generic.ObjectEditView):
    queryset = CdnSite.objects.all()
    model_form = forms.TenantForm
    template_name = "tenancy/tenant_edit.html"


class TenantDeleteView(generic.ObjectDeleteView):
    queryset = CdnSite.objects.all()


class TenantBulkImportView(generic.BulkImportView):
    queryset = CdnSite.objects.all()
    table = tables.TenantTable


class TenantBulkEditView(generic.BulkEditView):
    queryset = CdnSite.objects.select_related("cdnsite_role")
    filterset = filters.TenantFilterSet
    table = tables.TenantTable
    form = forms.TenantBulkEditForm


class TenantBulkDeleteView(generic.BulkDeleteView):
    queryset = CdnSite.objects.select_related("cdnsite_role")
    filterset = filters.TenantFilterSet
    table = tables.TenantTable