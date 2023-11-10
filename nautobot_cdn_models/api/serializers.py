from rest_framework import serializers
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field

from nautobot.core.api import (
    ContentTypeField,
    NautobotModelSerializer,
    NotesSerializerMixin,
    ValidatedModelSerializer,
    TreeModelSerializerMixin,
    SerializedPKRelatedField,
    ValidatedModelSerializer,
)
from nautobot.core.api.utils import get_serializer_for_model
from nautobot.dcim.models import Location
from nautobot.extras.models import Tag
from nautobot.dcim.api.serializers import (
    LocationSerializer
)
from nautobot.extras.api.serializers import NautobotModelSerializer, ConfigContextSchemaSerializer
from nautobot.extras.utils import FeatureQuery

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
    local_context_schema = ConfigContextSchemaSerializer(required=False, allow_null=True)
    
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
            "location",
            "site",
            "cacheMemoryProfileId",
            "neighbor1",
            "neighbor1_preference",
            "neighbor2",
            "neighbor2_preference",
            "local_context_schema",
            "local_context_data",
        ]
        
class CdnSiteWithRedirectMapContextSerializer(CdnSiteSerializer):
    redirect_map_context = serializers.SerializerMethodField()

    class Meta(CdnSiteSerializer.Meta):
        fields = [CdnSiteSerializer.Meta.fields] + ["redirect_map_context"]

    @extend_schema_field(serializers.DictField)
    def get_redirect_map_context(self, obj):
        return obj.get_redirect_map_context()

class RedirectMapContextSerializer(ValidatedModelSerializer, NotesSerializerMixin):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_cdn_models-api:redirectmapcontext-detail")
    owner_content_type = ContentTypeField(
        queryset=ContentType.objects.filter(FeatureQuery("config_context_owners").get_query()),
        required=False,
        allow_null=True,
        default=None,
    )
    owner = serializers.SerializerMethodField(read_only=True)
    schema = ConfigContextSchemaSerializer(required=False, allow_null=True)
    locations = SerializedPKRelatedField(
        queryset=Location.objects.all(),
        serializer=LocationSerializer,
        required=False,
        many=True,
    )
    cdnsites = SerializedPKRelatedField(
        queryset=models.CdnSite.objects.all(),
        serializer=nested_serializers.NestedCdnSiteSerializer,
        required=False,
        many=True,
    )
    cdn_site_roles = SerializedPKRelatedField(
        queryset=models.SiteRole.objects.all(),
        serializer=nested_serializers.NestedSiteRoleSerializer,
        required=False,
        many=True,
    )
    tags = serializers.SlugRelatedField(queryset=Tag.objects.all(), slug_field="slug", required=False, many=True)


    # Conditional enablement of dynamic groups filtering
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)


    class Meta:
        model = models.RedirectMapContext
        fields = [
            "url",
            "name",
            "owner_content_type",
            "owner_object_id",
            "owner",
            "weight",
            "description",
            "schema",
            "is_active",
            "locations",
            "cdnsites",
            "cdn_site_roles",
            "tags",
            "data",
        ]

    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_owner(self, obj):
        if obj.owner is None:
            return None
        serializer = get_serializer_for_model(obj.owner, prefix="Nested")
        context = {"request": self.context["request"]}
        return serializer(obj.owner, context=context).data