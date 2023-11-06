from django_tables2 import RequestConfig

from nautobot.core.views import generic, mixins as view_mixins
from nautobot.core.models.querysets import count_related
from nautobot.core.views.paginator import EnhancedPaginator, get_paginate_count
from nautobot.dcim.models import Device, Location, Rack, RackReservation
from nautobot.ipam.models import IPAddress, Prefix
from nautobot.virtualization.models import VirtualMachine

from nautobot.extras.models import RelationshipAssociation
from nautobot.extras.tables import RelationshipAssociationTable
from . import filters, tables, forms
from .models import CdnSite, HyperCacheMemoryProfile, SiteRole, RedirectMapContext


## HyperCache Memory Profiles
class HyperCacheMemoryProfileListView(generic.ObjectListView):
    queryset = HyperCacheMemoryProfile.objects.all()
    filterset = filters.HyperCacheMemoryProfileFilterSet
    table = tables.HyperCacheMemoryProfileTable


class HyperCacheMemoryProfileView(generic.ObjectView):
    queryset = HyperCacheMemoryProfile.objects.all()


class HyperCacheMemoryProfileEditView(generic.ObjectEditView):
    queryset = HyperCacheMemoryProfile.objects.all()
    model_form = forms.HyperCacheMemoryProfileForm


class HyperCacheMemoryProfileDeleteView(generic.ObjectDeleteView):
    queryset = HyperCacheMemoryProfile.objects.all()


class HyperCacheMemoryProfileBulkImportView(generic.BulkImportView):
    queryset = HyperCacheMemoryProfile.objects.all()
    table = tables.HyperCacheMemoryProfileTable


class HyperCacheMemoryProfileBulkDeleteView(generic.BulkDeleteView):
    queryset = HyperCacheMemoryProfile.objects.all()
    table = tables.HyperCacheMemoryProfileTable
    filterset = filters.HyperCacheMemoryProfileFilterSet

## CDN Site Roles ##
class SiteRoleListView(generic.ObjectListView):
    queryset = SiteRole.objects.annotate(cdnsite_count=count_related(CdnSite, "cdn_site_role"))
    filterset = filters.SiteRoleFilterSet
    table = tables.SiteRoleTable


class SiteRoleView(generic.ObjectView):
    queryset = SiteRole.objects.all()

    def get_extra_context(self, request, instance):
        # CdnSite
        cdnsites = CdnSite.objects.restrict(request.user, "view").filter(
            cdn_site_role__in=instance.descendants(include_self=True)
        )

        cdnsite_table = tables.CdnSiteTable(cdnsites)
        cdnsite_table.columns.hide("cdn_site_role")

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
    queryset = SiteRole.objects.annotate(cdnsite_count=count_related(CdnSite, "cdn_site_role"))
    table = tables.SiteRoleTable
    filterset = filters.SiteRoleFilterSet

## CDN SITES ##
class CdnSiteListView(generic.ObjectListView):
    queryset = CdnSite.objects.select_related("cdn_site_role")
    filterset = filters.CdnSiteFilterSet
    filterset_form = forms.CdnSiteFilterForm
    table = tables.CdnSiteTable


class CdnSiteView(generic.ObjectView):
    queryset = CdnSite.objects.select_related("cdn_site_role")

    # def get_extra_context(self, request, instance):
    #     stats = {
    #         # TODO: Should we include child locations of the filtered locations in the location_count below?
    #         "location_count": Location.objects.restrict(request.user, "view").filter(cdnsites=instance).count(),
    #         "rack_count": Rack.objects.restrict(request.user, "view").filter(cdnsites=instance).count(),
    #         "rackreservation_count": RackReservation.objects.restrict(request.user, "view")
    #         .filter(cdnsites=instance)
    #         .count(),
    #         "device_count": Device.objects.restrict(request.user, "view").filter(cdnsites=instance).count(),
    #         "prefix_count": Prefix.objects.restrict(request.user, "view").filter(cdnsites=instance).count(),
    #         "ipaddress_count": IPAddress.objects.restrict(request.user, "view").filter(cdnsites=instance).count(),
    #         "virtualmachine_count": VirtualMachine.objects.restrict(request.user, "view")
    #         .filter(cdnsites=instance)
    #         .count(),
    #     }

    #     return {
    #         "stats": stats,
    #     }
    def get_extra_context(self, request, instance):
        stats = {
            "device_count": RelationshipAssociation.objects.all().filter(destination_id=instance.id).count()
        }
        return{
            "stats": stats
        }
    
    def get_extra_context(self, request, instance):
        relations = RelationshipAssociation.objects.all().filter(destination_id=instance.id)

        relation_table = RelationshipAssociationTable(relations)
        relation_table.columns.hide("destination")

        paginate = {
            "paginator_class": EnhancedPaginator,
            "per_page": get_paginate_count(request),
        }
        RequestConfig(request, paginate).configure(relation_table)

        return {
            "relation_table": relation_table
        }


class CdnSiteEditView(generic.ObjectEditView):
    queryset = CdnSite.objects.all()
    model_form = forms.CdnSiteForm
    template_name = "nautobot_cdn_models/cdnsite_edit.html"


class CdnSiteDeleteView(generic.ObjectDeleteView):
    queryset = CdnSite.objects.all()


class CdnSiteBulkImportView(generic.BulkImportView):
    queryset = CdnSite.objects.all()
    table = tables.CdnSiteTable


class CdnSiteBulkEditView(generic.BulkEditView):
    queryset = CdnSite.objects.select_related("cdn_site_role")
    filterset = filters.CdnSiteFilterSet
    table = tables.CdnSiteTable
    form = forms.CdnSiteBulkEditForm


class CdnSiteBulkDeleteView(generic.BulkDeleteView):
    queryset = CdnSite.objects.select_related("cdn_site_role")
    filterset = filters.CdnSiteFilterSet
    table = tables.CdnSiteTable
    
class RedirectMapContextListView(generic.ObjectListView):
    queryset = RedirectMapContext.objects.all()
    filterset = filters.RedirectMapContextFilterSet
    filterset_form = forms.RedirectMapContextFilterForm
    table = tables.RedirectMapContextTable
    action_buttons = ("add",)


class RedirectMapContextView(generic.ObjectView):
    queryset = RedirectMapContext.objects.all()

    def get_extra_context(self, request, instance):
        # Determine user's preferred output format
        if request.GET.get("format") in ["json", "yaml"]:
            format_ = request.GET.get("format")
            if request.user.is_authenticated:
                request.user.set_config("redirectmapcontext.format", format_, commit=True)
        elif request.user.is_authenticated:
            format_ = request.user.get_config("redirectmapcontext.format", "json")
        else:
            format_ = "json"

        return {
            "format": format_,
        }

    
class RedirectMapContextEditView(generic.ObjectEditView):
    queryset = RedirectMapContext.objects.all()
    model_form = forms.RedirectMapContextForm
    template_name = "nautobot_cdn_models/redirectmapcontext_edit.html"


class RedirectMapContextBulkEditView(generic.BulkEditView):
    queryset = RedirectMapContext.objects.all()
    filterset = filters.RedirectMapContextFilterSet
    table = tables.RedirectMapContextTable
    form = forms.RedirectMapContextBulkEditForm


class RedirectMapContextDeleteView(generic.ObjectDeleteView):
    queryset = RedirectMapContext.objects.all()


class RedirectMapContextBulkDeleteView(generic.BulkDeleteView):
    queryset = RedirectMapContext.objects.all()
    table = tables.RedirectMapContextTable


# define a merger with a custom list merge strategy
list_merger = Merger(
    # pass in a list of tuple, with the "strategy" as the first element and the "type" as the second element
    [
        (list, ["append"]),
        (dict, ["merge"])
    ],
    ["override"],
    ["override"]
)

class ObjectRedirectMapContextView(generic.ObjectView):
    base_template = None
    template_name = "nautobot_cdn_models/object_redirectmapcontext.html"

    def get_extra_context(self, request, instance):
        source_contexts = RedirectMapContext.objects.restrict(request.user, "view").get_for_object(instance)
        # Merge the context data
        merged_data = {}
        for context in source_contexts:
            merged_data = list_merger.merge(merged_data, context.data)

        # Determine user's preferred output format
        if request.GET.get("format") in ["json", "yaml"]:
            format_ = request.GET.get("format")
            if request.user.is_authenticated:
                request.user.set_config("redirectmapcontext.format", format_, commit=True)
        elif request.user.is_authenticated:
            format_ = request.user.get_config("redirectmapcontext.format", "json")
        else:
            format_ = "json"

        return {
            "rendered_context": merged_data,  # return the merged data instead
            "source_contexts": source_contexts,
            "format": format_,
            "base_template": self.base_template,
            "active_tab": "config-context",
        }

class CdnSiteConfigContextView(ObjectRedirectMapContextView):
    queryset = CdnSite.objects.annotate_config_context_data()
    base_template = "nautobot_akamai_models/cdnsite.html"