from nautobot.extras import filters
from . import serializers

from nautobot.extras.api.views import NautobotModelViewSet
from nautobot.core.api.filter_backends import NautobotFilterBackend
from nautobot.core.api.views import (
    ModelViewSet,
)
from nautobot.extras.api.views import NautobotModelViewSet

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


class RedirectMapContextFilterBackend(NautobotFilterBackend):
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


class RedirectMapContextQuerySetMixin:
    """
    Used by views that work with config context models (device and virtual machine).
    Provides a get_queryset() method which deals with adding the config context
    data annotation or not.
    """

    filter_backends = [RedirectMapContextFilterBackend]

    def get_queryset(self):
        """
        Build the proper queryset based on the request context

        If the `brief` query param equates to True or the `exclude` query param
        includes `config_context` as a value, return the base queryset.

        Else, return the queryset annotated with config context data
        """
        queryset = super().get_queryset()
        request = self.get_serializer_context()["request"]
        if self.brief or (request is not None and "redirect_map_context" in request.query_params.get("exclude", [])):
            return queryset
        return queryset.annotate_config_context_data()


class RedirectMapContextViewSet(ModelViewSet):
    queryset = models.RedirectMapContext.objects.prefetch_related(
        "regions",
        "cdnsites",
        "cdn_site_roles",
    )
    serializer_class = serializers.RedirectMapContextSerializer
    filterset_class = filters.RedirectMapContextFilterSet