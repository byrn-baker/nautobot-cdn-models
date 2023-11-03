from rest_framework import serializers
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from nautobot.core.api import TreeModelSerializerMixin
from nautobot.dcim.models import Location
from nautobot.dcim.api.serializers import (
    LocationSerializer
)
from nautobot.extras.api.serializers import NautobotModelSerializer
# from nautobot.extras.api.nested_serializers import (
#     NestedConfigContextSchemaSerializer,
# )

from .. import models

from . import nested_serializers


class HyperCacheMemoryProfileSerializer(NautobotModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_cdn_models-api:hypercachememoryprofile-detail"
    )
    class Meta:
        model = models.HyperCacheMemoryProfile
        fields = "__all__"


class SiteRoleSerializer(NautobotModelSerializer, TreeModelSerializerMixin):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_cdn_models-api:siterole-detail"
    )
    cdnsite_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.SiteRole
        fields = "__all__"
        list_display_fields = ["name", "cdnsite_count", "description", "actions"]


class CdnSiteSerializer(NautobotModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_cdn_models-api:cdnsite-detail"
    )
    cdn_site_role = nested_serializers.NestedSiteRoleSerializer(required=False, allow_null=True)
    location = LocationSerializer(required=False, allow_null=True)
    cacheMemoryProfileId = nested_serializers.NestedHyperCacheMemoryProfileSerializer(required=False, allow_null=True)
    device_count = serializers.IntegerField(read_only=True)
    ipaddress_count = serializers.IntegerField(read_only=True)
    prefix_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)
    # neighbor1 = nested_serializers.NestedCdnSiteSerializer()
    # neighbor2 = nested_serializers.NestedCdnSiteSerializer(required=False, allow_null=True)
    # local_context_schema = NestedConfigContextSchemaSerializer(required=False, allow_null=True)
    
    class Meta:
        model = models.CdnSite
        fields = "__all__"
        list_display_fields = [
            "url",
            "name",
            "status",
            "abbreviatedName",
            "bandwidthLimitMbps",
            "enableDisklessMode",
            "siteId",
            "cdn_site_role",
            "region",
            "site",
            "cacheMemoryProfileId",
            "neighbor1",
            "neighbor1_preference",
            "neighbor2",
            "neighbor2_preference",
        ]