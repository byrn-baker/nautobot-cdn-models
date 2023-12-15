from nautobot.extras import filters
from . import serializers

from nautobot.extras.api.views import NautobotModelViewSet
from nautobot.core.api.filter_backends import NautobotFilterBackend
from nautobot.core.api.views import (
    ModelViewSet,
)
from nautobot.extras.api.views import NautobotModelViewSet, NotesViewSetMixin

from .. import models, filters
from . import serializers


class HyperCacheMemoryProfileViewSet(NautobotModelViewSet):
    queryset = models.HyperCacheMemoryProfile.objects.all()
    serializer_class = serializers.HyperCacheMemoryProfileSerializer
    filter_class = filters.HyperCacheMemoryProfileFilterSet

class SiteRoleViewSet(NautobotModelViewSet):
    queryset = models.SiteRole.objects.all()
    serializer_class = serializers.SiteRoleSerializer
    filterset_class = filters.SiteRoleFilterSet

class CdnSiteViewSet(NautobotModelViewSet):
    queryset = models.CdnSite.objects.all()
    serializer_class = serializers.CdnSiteSerializer
    filter_class = filters.CdnSiteFilterSet

#
# Config contexts
#


class CdnConfigContextFilterBackend(NautobotFilterBackend):
    """
    Used by views that work with config context models (device and virtual machine).

    Recognizes that "exclude" is not a filterset parameter but rather a view parameter (see ConfigContextQuerySetMixin)
    """

    def get_filterset_kwargs(self, request, queryset, view):
        kwargs = super().get_filterset_kwargs(request, queryset, view)
        try:
            kwargs["data"].pop("exclude")
        except KeyError:
            pass
        return kwargs


class CdnConfigContextQuerySetMixin:
    """
    Used by views that work with config context models (device and virtual machine).
    Provides a get_queryset() method which deals with adding the config context
    data annotation or not.
    """

    filter_backends = [CdnConfigContextFilterBackend]

    def get_queryset(self):
        """
        Build the proper queryset based on the request context

        If the `brief` query param equates to True or the `exclude` query param
        includes `config_context` as a value, return the base queryset.

        Else, return the queryset annotated with config context data
        """
        queryset = super().get_queryset()
        request = self.get_serializer_context()["request"]
        if self.brief or (request is not None and "cdnconfig_context" in request.query_params.get("exclude", [])):
            return queryset
        return queryset.annotate_config_context_data()


class CdnConfigContextViewSet(ModelViewSet, NotesViewSetMixin):
    queryset = models.CdnConfigContext.objects.prefetch_related(
        "regions",
        "cdnsites",
        "cdn_site_roles",
        "failover_site",
    )
    serializer_class = serializers.CdnConfigContextSerializer
    filterset_class = filters.CdnConfigContextFilterSet


#
# Content Delivery
#

class ServiceProviderViewSet(NautobotModelViewSet):
    queryset = models.ServiceProvider.objects.all()
    serializer_class = serializers.ServiceProviderSerializer
    filter_class = filters.ServiceProviderFilterSet
    
class ContentProviderViewSet(NautobotModelViewSet):
    queryset = models.ContentProvider.objects.all()
    serializer_class = serializers.ContentProviderSerializer
    filter_class = filters.ContentProviderFilterSet
class OriginViewSet(NautobotModelViewSet):
    queryset = models.Origin.objects.all()
    serializer_class = serializers.OriginSerializer
    filter_class = filters.OriginFilterSet

class CdnPrefixViewSet(NautobotModelViewSet):
    queryset = models.CdnPrefix.objects.all()
    serializer_class = serializers.CdnPrefixSerializer
    filter_class = filters.CdnPrefixFilterSet

class CdnPrefixDefaultBehaviorViewSet(NautobotModelViewSet):
    queryset = models.CdnPrefixDefaultBehavior.objects.all()
    serializer_class = serializers.CdnPrefixDefaultBehaviorSerializer
    filter_class = filters.CdnPrefixDefaultBehaviorFilterSet

class CdnPrefixBehaviorViewSet(NautobotModelViewSet):
    queryset = models.CdnPrefixBehavior.objects.all()
    serializer_class = serializers.CdnPrefixBehaviorSerializer
    filter_class = filters.CdnPrefixBehaviorFilterSet
