from rest_framework import serializers
from nautobot.core.api import WritableNestedSerializer
from .. import models

class NestedHyperCacheMemoryProfileSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_cdn_models-api:hypercachememoryprofile-detail"
    )

    class Meta:
        model = models.HyperCacheMemoryProfile
        fields = "__all__"

class NestedSiteRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_cdn_models-api:siterole-detail"
    )

    class Meta:
        model = models.SiteRole
        fields = "__all__"

class NestedCdnSiteSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_cdn_models-api:cdnsite-detail"
    )

    class Meta:
        model = models.CdnSite
        fields = "__all__"

class NestedRedirectMapContexttSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_cdn_models-api:redirectmapcontext-detail")

    class Meta:
        model = models.RedirectMapContext
        fields = ["id", "url", "name"]