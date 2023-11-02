from jsonschema.validators import Draft7Validator
from django_tables2 import RequestConfig
from deepmerge import Merger


from nautobot.core.views import mixins as view_mixins
from nautobot.core.views import generic
from nautobot.extras.views import ObjectChangeLogView
from nautobot.extras.models import RelationshipAssociation
from nautobot.utilities.tables import ButtonsColumn
from nautobot.utilities.paginator import EnhancedPaginator, get_paginate_count

from nautobot.extras.tables import RelationshipAssociationTable

from .models import (
    HyperCacheMemoryProfile,
    SiteRole,
    CdnSite,
    CdnConfigContext
)

from . import ( 
    filters, 
    forms, 
    tables,
)
from .api import serializers

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

  
class SiteRoleView(generic.ObjectView):
    queryset = SiteRole.objects.all()
    def get_extra_context(self, request, instance):
        cdnsites = CdnSite.objects.all().filter(cdn_site_role__in=instance.get_descendants(include_self=True))

        cdnsite_table = tables.CdnSiteTable(cdnsites)
        cdnsite_table.columns.hide("cdn_site_role")

        paginate = {
            "paginator_class": EnhancedPaginator,
            "per_page": get_paginate_count(request),
        }
        RequestConfig(request, paginate).configure(cdnsite_table)

        return {
            "cdnsite_table": cdnsite_table
        }
class SiteRoleListView(generic.ObjectListView):
    queryset = SiteRole.objects.add_related_count(
        SiteRole.objects.all(), CdnSite, "cdn_site_role", "cdnsite_count", cumulative=True
    )
    filterset = filters.SiteRoleFilterSet
    table = tables.SiteRoleTable

class SiteRoleEditView(generic.ObjectEditView):
    queryset = SiteRole.objects.all()
    model_form = forms.SiteRoleForm


class SiteRoleDeleteView(generic.ObjectDeleteView):
    queryset = SiteRole.objects.all()

class SiteRoleBulkImportView(generic.BulkImportView):
    queryset = SiteRole.objects.all()
    model_form = forms.SiteRoleCSVForm
    table = tables.SiteRoleTable

class SiteRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = SiteRole.objects.add_related_count(
        SiteRole.objects.all(), CdnSite, "cdn_site_role", "cdnsite_count", cumulative=True
    )
    table = tables.SiteRoleTable

class CdnSiteUIViewSet(
    view_mixins.ObjectListViewMixin,
    view_mixins.ObjectDetailViewMixin,
    view_mixins.ObjectEditViewMixin,
    view_mixins.ObjectDestroyViewMixin,
    view_mixins.ObjectBulkDestroyViewMixin,
):
    queryset = CdnSite.objects.all()
    table_class = tables.CdnSiteTable
    form_class = forms.CdnSiteForm
    filterset_class = filters.CdnSiteFilterSet
    filterset_form_class = forms.CdnSiteFilterForm
    serializer_class = serializers.CdnSiteSerializer
    action_buttons = ("add",)

class CdnSiteListView(generic.ObjectListView):
    queryset = CdnSite.objects.all()
    filterset = filters.CdnSiteFilterSet
    filterset_form = forms.CdnSiteFilterForm
    table = tables.CdnSiteTable


class CdnSiteView(generic.ObjectView):
    queryset = CdnSite.objects.select_related("region", "cdn_site_role", "status")
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
    model_form = forms.CdnSiteCSVForm
    table = tables.CdnSiteTable

class CdnSiteBulkEditView(generic.BulkEditView):
    queryset = CdnSite.objects.select_related("region", "cdn_site_role")
    filterset = filters.CdnSiteFilterSet
    table = tables.CdnSiteTable
    form = forms.CdnSiteBulkEditForm

class CdnSiteBulkDeleteView(generic.BulkDeleteView):
    queryset = CdnSite.objects.select_related("region", "cdn_site_role")
    filterset = filters.CdnSiteFilterSet
    table = tables.CdnSiteTable

class CdnSiteChangeLogView(ObjectChangeLogView):
    base_template = "nautobot_akamai_models/cdnsite.html"

#
# Config contexts
#

# TODO(Glenn): disallow (or at least warn) user from manually editing config contexts that
# have an associated owner, such as a Git repository


class CdnConfigContextListView(generic.ObjectListView):
    queryset = CdnConfigContext.objects.all()
    filterset = filters.CdnConfigContextFilterSet
    filterset_form = forms.CdnConfigContextFilterForm
    table = tables.CdnConfigContextTable
    action_buttons = ("add",)


class CdnConfigContextView(generic.ObjectView):
    queryset = CdnConfigContext.objects.all()

    def get_extra_context(self, request, instance):
        # Determine user's preferred output format
        if request.GET.get("format") in ["json", "yaml"]:
            format_ = request.GET.get("format")
            if request.user.is_authenticated:
                request.user.set_config("cdnconfigcontext.format", format_, commit=True)
        elif request.user.is_authenticated:
            format_ = request.user.get_config("cdnconfigcontext.format", "json")
        else:
            format_ = "json"

        return {
            "format": format_,
        }

    
class CdnConfigContextEditView(generic.ObjectEditView):
    queryset = CdnConfigContext.objects.all()
    model_form = forms.CdnConfigContextForm
    template_name = "nautobot_cdn_models/cdnconfigcontext_edit.html"


class CdnConfigContextBulkEditView(generic.BulkEditView):
    queryset = CdnConfigContext.objects.all()
    filterset = filters.CdnConfigContextFilterSet
    table = tables.CdnConfigContextTable
    form = forms.CdnConfigContextBulkEditForm


class CdnConfigContextDeleteView(generic.ObjectDeleteView):
    queryset = CdnConfigContext.objects.all()


class CdnConfigContextBulkDeleteView(generic.BulkDeleteView):
    queryset = CdnConfigContext.objects.all()
    table = tables.CdnConfigContextTable


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

class ObjectCdnConfigContextView(generic.ObjectView):
    base_template = None
    template_name = "nautobot_cdn_models/object_cdnconfigcontext.html"

    def get_extra_context(self, request, instance):
        source_contexts = CdnConfigContext.objects.restrict(request.user, "view").get_for_object(instance)
        # Merge the context data
        merged_data = {}
        for context in source_contexts:
            merged_data = list_merger.merge(merged_data, context.data)

        # Determine user's preferred output format
        if request.GET.get("format") in ["json", "yaml"]:
            format_ = request.GET.get("format")
            if request.user.is_authenticated:
                request.user.set_config("cdnconfigcontext.format", format_, commit=True)
        elif request.user.is_authenticated:
            format_ = request.user.get_config("cdnconfigcontext.format", "json")
        else:
            format_ = "json"

        return {
            "rendered_context": merged_data,  # return the merged data instead
            "source_contexts": source_contexts,
            "format": format_,
            "base_template": self.base_template,
            "active_tab": "config-context",
        }

class CdnSiteConfigContextView(ObjectCdnConfigContextView):
    queryset = CdnSite.objects.annotate_config_context_data()
    base_template = "nautobot_akamai_models/cdnsite.html"

#
# Config context schemas
#

# TODO(Glenn): disallow (or at least warn) user from manually editing config context schemas that
# have an associated owner, such as a Git repository


# class CdnConfigContextSchemaListView(generic.ObjectListView):
#     queryset = CdnConfigContextSchema.objects.all()
#     filterset = filters.CdnConfigContextSchemaFilterSet
#     filterset_form = forms.CdnConfigContextSchemaFilterForm
#     table = tables.CdnConfigContextSchemaTable
#     action_buttons = ("add",)


# class CdnConfigContextSchemaView(generic.ObjectView):
#     queryset = CdnConfigContextSchema.objects.all()

#     def get_extra_context(self, request, instance):
#         # Determine user's preferred output format
#         if request.GET.get("format") in ["json", "yaml"]:
#             format_ = request.GET.get("format")
#             if request.user.is_authenticated:
#                 request.user.set_config("cdnconfigcontextschema.format", format_, commit=True)
#         elif request.user.is_authenticated:
#             format_ = request.user.get_config("cdnconfigcontextschema.format", "json")
#         else:
#             format_ = "json"

#         return {
#             "format": format_,
#         }


# class CdnConfigContextSchemaObjectValidationView(generic.ObjectView):
#     """
#     This view renders a detail tab that shows tables of objects that utilize the given schema object
#     and their validation state.
#     """

#     queryset = CdnConfigContextSchema.objects.all()
#     template_name = "nautobot_cdn_models/cdnconfigcontextschema_validation.html"

#     def get_extra_context(self, request, instance):
#         """
#         Reuse the model tables for config context, device, and virtual machine but inject
#         the `CdnConfigContextSchemaValidationStateColumn` and an object edit action button.
#         """
#         # Prep the validator with the schema so it can be reused for all records
#         validator = Draft7Validator(instance.data_schema)

#         # Config context table
#         config_context_table = tables.CdnConfigContextTable(
#             data=instance.CdnConfigContext_set.all(),
#             orderable=False,
#             extra_columns=[
#                 (
#                     "validation_state",
#                     tables.CdnConfigContextSchemaValidationStateColumn(validator, "data", empty_values=()),
#                 ),
#                 ("actions", ButtonsColumn(model=CdnConfigContext, buttons=["edit"])),
#             ],
#         )
#         paginate = {
#             "paginator_class": EnhancedPaginator,
#             "per_page": get_paginate_count(request),
#         }
#         RequestConfig(request, paginate).configure(config_context_table)

#         # CdnSite table
#         cdnsite_table = tables.CdnSiteTable(
#             data=instance.cdnsite_set.select_related(
#                 "region",
#                 "cdn_site_role",
#             ),
#             orderable=False,
#             extra_columns=[
#                 (
#                     "validation_state",
#                     tables.CdnConfigContextSchemaValidationStateColumn(validator, "local_context_data", empty_values=()),
#                 ),
#                 ("actions", ButtonsColumn(model=CdnSite, buttons=["edit"])),
#             ],
#         )
#         paginate = {
#             "paginator_class": EnhancedPaginator,
#             "per_page": get_paginate_count(request),
#         }
#         RequestConfig(request, paginate).configure(cdnsite_table)

#         return {
#             "config_context_table": config_context_table,
#             "device_table": cdnsite_table,
#             "active_tab": "validation",
#         }


# class CdnConfigContextSchemaEditView(generic.ObjectEditView):
#     queryset = CdnConfigContextSchema.objects.all()
#     model_form = forms.CdnConfigContextSchemaForm
#     template_name = "nautobot_cdn_models/cdnconfigcontextschema_edit.html"


# class CdnConfigContextSchemaBulkEditView(generic.BulkEditView):
#     queryset = CdnConfigContextSchema.objects.all()
#     filterset = filters.CdnConfigContextSchemaFilterSet
#     table = tables.CdnConfigContextSchemaTable
#     form = forms.CdnConfigContextSchemaBulkEditForm


# class CdnConfigContextSchemaDeleteView(generic.ObjectDeleteView):
#     queryset = CdnConfigContextSchema.objects.all()


# class CdnConfigContextSchemaBulkDeleteView(generic.BulkDeleteView):
#     queryset = CdnConfigContextSchema.objects.all()
#     table = tables.CdnConfigContextSchemaTable