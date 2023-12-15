from jsonschema.validators import Draft7Validator
from django_tables2 import RequestConfig
from django.views.generic.detail import DetailView
from deepmerge import Merger
import json
import requests
from datadog import initialize, api
from html.parser import HTMLParser


from nautobot.core.views import mixins as view_mixins
from nautobot.core.views import generic
from nautobot.extras.views import ObjectChangeLogView
from nautobot.extras.models import RelationshipAssociation
from nautobot.utilities.tables import ButtonsColumn
from nautobot.utilities.paginator import EnhancedPaginator, get_paginate_count

from nautobot.dcim.models import Device

from nautobot.extras.tables import RelationshipAssociationTable

from .models import (
    HyperCacheMemoryProfile,
    SiteRole,
    CdnSite,
    CdnConfigContext,
    ServiceProvider,
    ContentProvider,
    Origin,
    CdnPrefix,
    CdnPrefixDefaultBehavior,
    CdnPrefixBehavior
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
    lookup_field = "pk"
  
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

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'iframe':
            for attr in attrs:
                if attr[0] == 'src':
                    self.iframe_src = attr[1]
                    
class CdnSiteView(generic.ObjectView):
    queryset = CdnSite.objects.select_related("region", "cdn_site_role", "status")
    
    def get_datadog_graph(self, cdnsite_name):
        region, site_name, state, streamtype, tier = cdnsite_name.split('_')
        # Setup the correct query
        if 'shield' in cdnsite_name:
            query = f"sum:akamai_aura.origin.sent_bw{{env:prod,streamtype:{streamtype.lower()},siteloc:{site_name.lower()}}} by {{siteloc}}.rollup(max, 60) * 1000000"
        elif 'mid' in cdnsite_name:
            query = f"sum:akamai_aura.mid.sent_bw{{env:prod,streamtype:{streamtype.lower()},siteloc:{site_name.lower()}}} by {{siteloc}}.rollup(max, 60) * 1000000"
        else:
            query = f"sum:akamai_aura.sent_bw{{env:prod,streamtype:{streamtype.lower()},siteloc:{site_name.lower()}}} by {{siteloc}}.rollup(max, 60) * 1000000"
        # Initialize request parameters with Datadog API/APP key
        options = {
            'api_host': 'https://charter-ipvc.datadoghq.com/',
            'api_key': '11e1df945b0fce8b5b2422b57ce889e5',
            'app_key': '225bf34f541e97825f0b40aec3cf658a9490ce23'
        }

        initialize(**options)

        graph_json = {
            "requests": [{
                "q": query
            }],
            "viz": "timeseries",
            "events": []
        }
        graph_json = json.dumps(graph_json)

        embed = api.Embed.create(
            graph_json=graph_json,
            timeframe="1_week",
            size="large",
            legend="yes"
        )

        parser = MyHTMLParser()
        parser.feed(embed['html'])
        datadog_graph_url = parser.iframe_src

        return {
            "datadog_graph_url": datadog_graph_url  # Only return the URL for the Datadog graph
        }
    
    def get_extra_context(self, request, instance):
        datadog_graph = self.get_datadog_graph(instance.name)
        datadog_graph_url = datadog_graph['datadog_graph_url']
        stats = {
            "device_count": RelationshipAssociation.objects.all().filter(destination_id=instance.id).count()
        }
        relations = RelationshipAssociation.objects.all().filter(destination_id=instance.id)

        relation_table = RelationshipAssociationTable(relations)
        relation_table.columns.hide("destination")

        paginate = {
            "paginator_class": EnhancedPaginator,
            "per_page": get_paginate_count(request),
        }
        RequestConfig(request, paginate).configure(relation_table)
        return{
            "stats": stats,
            "relation_table": relation_table,
            "datadog_graph_url": datadog_graph_url,
        }

class DeviceDetailPluginView(generic.ObjectView):
    queryset = Device.objects.all()
    template_name = "nautobot_cdn_models/device_detail_tab.html"
    
    def get_datadog_graph(self, device_name):
        device = device_name.replace(".spectrum.com", "")
        options = {
            'api_key': '11e1df945b0fce8b5b2422b57ce889e5',
            'app_key': '225bf34f541e97825f0b40aec3cf658a9490ce23',
            'api_host': 'https://charter-ipvc.datadoghq.com/'
        }
        if 'shc0' in device_name:
            query = f"sum:akamai_aura.origin.sent_bw{{env:prod,streamtype:vod,host:{device}}} by {{host}} * 1000000"
        elif 'shc1' in device_name:
            query = f"sum:akamai_aura.origin.sent_bw{{env:prod,streamtype:linear,host:{device}}} by {{host}} * 1000000"
        elif 'mid' in device_name:
            query = f"sum:akamai_aura.mid.sent_bw{{env:prod,streamtype:linear,host:{device}}} by {{host}} * 1000000"
        elif 'hpc0' in device_name:
            query = f"sum:akamai_aura.sent_bw{{env:prod,streamtype:vod,host:{device}}} by {{host}} * 1000000"
        elif 'hpc1' in device_name:
            query = f"sum:akamai_aura.sent_bw{{env:prod,streamtype:linear,host:{device}}} by {{host}} * 1000000"

        initialize(**options)

        graph_json = {
            "requests": [{
                "q": query
            }],
            "viz": "timeseries",
            "events": []
        }
        graph_json = json.dumps(graph_json)

        embed = api.Embed.create(
            graph_json=graph_json,
            timeframe="1_week",
            size="large",
            legend="yes"
        )

        parser = MyHTMLParser()
        parser.feed(embed['html'])
        datadog_graph_url = parser.iframe_src

        return {
            "datadog_graph_url": datadog_graph_url  # Only return the URL for the Datadog graph
        }
        
    def get_extra_context(self, request, instance):
        datadog_graph = self.get_datadog_graph(instance.name)
        datadog_graph_url = datadog_graph['datadog_graph_url']
        
        return{
            "datadog_graph_url": datadog_graph_url,
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
# Content Delivery
#

class ServiceProviderUIViewSet(
    view_mixins.ObjectListViewMixin,
    view_mixins.ObjectDetailViewMixin,
    view_mixins.ObjectEditViewMixin,
    view_mixins.ObjectDestroyViewMixin,
    view_mixins.ObjectBulkDestroyViewMixin,
):
    queryset = ServiceProvider.objects.all()
    table_class = tables.ServiceProviderTable
    form_class = forms.ServiceProviderForm
    filterset_class = filters.ServiceProviderFilterSet
    filterset_form_class = forms.ServiceProviderFilterForm
    serializer_class = serializers.ServiceProviderSerializer
    action_buttons = ("add",)
    lookup_field = "pk"

class ContentProviderUIViewSet(
    view_mixins.ObjectListViewMixin,
    view_mixins.ObjectDetailViewMixin,
    view_mixins.ObjectEditViewMixin,
    view_mixins.ObjectDestroyViewMixin,
    view_mixins.ObjectBulkDestroyViewMixin,
):
    queryset = ContentProvider.objects.all()
    table_class = tables.ContentProviderTable
    form_class = forms.ContentProviderForm
    filterset_class = filters.ContentProviderFilterSet
    filterset_form_class = forms.ContentProviderFilterForm
    serializer_class = serializers.ContentProviderSerializer
    action_buttons = ("add",)
    lookup_field = "pk"

class OriginUIViewSet(
    view_mixins.ObjectListViewMixin,
    view_mixins.ObjectDetailViewMixin,
    view_mixins.ObjectEditViewMixin,
    view_mixins.ObjectDestroyViewMixin,
    view_mixins.ObjectBulkDestroyViewMixin,
):
    queryset = Origin.objects.all()
    table_class = tables.OriginTable
    form_class = forms.OriginForm
    filterset_class = filters.OriginFilterSet
    filterset_form_class = forms.OriginFilterForm
    serializer_class = serializers.OriginSerializer
    action_buttons = ("add",)
    lookup_field = "pk"

class CdnPrefixUIViewSet(
    view_mixins.ObjectListViewMixin,
    view_mixins.ObjectDetailViewMixin,
    view_mixins.ObjectEditViewMixin,
    view_mixins.ObjectDestroyViewMixin,
    view_mixins.ObjectBulkDestroyViewMixin,
):
    queryset = CdnPrefix.objects.all()
    table_class = tables.CdnPrefixTable
    form_class = forms.CdnPrefixForm
    filterset_class = filters.CdnPrefixFilterSet
    filterset_form_class = forms.CdnPrefixFilterForm
    serializer_class = serializers.CdnPrefixSerializer
    action_buttons = ("add",)
    lookup_field = "pk"
    
class CdnPrefixDefaultBehaviorUIViewSet(
    view_mixins.ObjectListViewMixin,
    view_mixins.ObjectDetailViewMixin,
    view_mixins.ObjectEditViewMixin,
    view_mixins.ObjectDestroyViewMixin,
    view_mixins.ObjectBulkDestroyViewMixin,
):
    queryset = CdnPrefixDefaultBehavior.objects.all()
    table_class = tables.CdnPrefixDefaultBehaviorTable
    form_class = forms.CdnPrefixDefaultBehaviorForm
    filterset_class = filters.CdnPrefixDefaultBehaviorFilterSet
    filterset_form_class = forms.CdnPrefixDefaultBehaviorFilterForm
    serializer_class = serializers.CdnPrefixDefaultBehaviorSerializer
    action_buttons = ("add",)
    lookup_field = "pk"

class CdnPrefixBehaviorUIViewSet(
    view_mixins.ObjectListViewMixin,
    view_mixins.ObjectDetailViewMixin,
    view_mixins.ObjectEditViewMixin,
    view_mixins.ObjectDestroyViewMixin,
    view_mixins.ObjectBulkDestroyViewMixin,
):
    queryset = CdnPrefixBehavior.objects.all()
    table_class = tables.CdnPrefixBehaviorTable
    form_class = forms.CdnPrefixBehaviorForm
    filterset_class = filters.CdnPrefixBehaviorFilterSet
    filterset_form_class = forms.CdnPrefixBehaviorFilterForm
    serializer_class = serializers.CdnPrefixBehaviorSerializer
    action_buttons = ("add",)
    lookup_field = "pk"
