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
