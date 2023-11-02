from rest_framework import serializers
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field

from nautobot.utilities.api import get_serializer_for_model
from nautobot.core.api import (
    ContentTypeField,
    SerializedPKRelatedField,
    ValidatedModelSerializer,
)
from nautobot.dcim.models import Region
from nautobot.dcim.api.nested_serializers import (
    NestedRegionSerializer,
    NestedSiteSerializer
)
from nautobot.extras.api.serializers import (
    NautobotModelSerializer,
    StatusModelSerializerMixin,
    NotesSerializerMixin
)
from nautobot.extras.api.nested_serializers import (
    NestedConfigContextSchemaSerializer,
)
from nautobot.extras.models import Tag

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


class SiteRoleSerializer(NautobotModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_cdn_models-api:siterole-detail"
    )

    class Meta:
        model = models.SiteRole
        fields = "__all__"


class CdnSiteSerializer(NautobotModelSerializer, StatusModelSerializerMixin):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_cdn_models-api:cdnsite-detail"
    )
    cdn_site_role = nested_serializers.NestedSiteRoleSerializer(required=False, allow_null=True)
    region = NestedRegionSerializer(required=False, allow_null=True)
    site = NestedSiteSerializer(required=False, allow_null=True)
    cacheMemoryProfileId = nested_serializers.NestedHyperCacheMemoryProfileSerializer(required=False, allow_null=True)
    # neighbor1 = nested_serializers.NestedCdnSiteSerializer()
    # neighbor2 = nested_serializers.NestedCdnSiteSerializer(required=False, allow_null=True)
    local_context_schema = NestedConfigContextSchemaSerializer(required=False, allow_null=True)
    
    class Meta:
        model = models.CdnSite
        fields = [
            "url",
            "name",
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
            "local_context_schema",
            "local_context_data",
        ]

class CdnSiteWithConfigContextSerializer(CdnSiteSerializer):
    cdn_config_context = serializers.SerializerMethodField()

    class Meta(CdnSiteSerializer.Meta):
        fields = CdnSiteSerializer.Meta.fields + ["cdn_config_context"]

    @extend_schema_field(serializers.DictField)
    def get_cdn_config_context(self, obj):
        return obj.get_cdn_config_context()

class CdnConfigContextSerializer(ValidatedModelSerializer, NotesSerializerMixin):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_cdn_models-api:cdnconfigcontext-detail")
    owner_content_type = ContentTypeField(
        queryset=ContentType.objects.filter(FeatureQuery("config_context_owners").get_query()),
        required=False,
        allow_null=True,
        default=None,
    )
    owner = serializers.SerializerMethodField(read_only=True)
    schema = NestedConfigContextSchemaSerializer(required=False, allow_null=True)
    regions = SerializedPKRelatedField(
        queryset=Region.objects.all(),
        serializer=NestedRegionSerializer,
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
        model = models.CdnConfigContext
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
            "regions",
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


#
# Config context Schemas
#


# class CdnConfigContextSchemaSerializer(NautobotModelSerializer):
#     url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_cdn_models-api:cdnconfigcontextschema-detail")
#     owner_content_type = ContentTypeField(
#         queryset=ContentType.objects.filter(FeatureQuery("config_context_owners").get_query()),
#         required=False,
#         allow_null=True,
#         default=None,
#     )
#     owner = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = models.CdnConfigContextSchema
#         fields = [
#             "url",
#             "name",
#             "slug",
#             "owner_content_type",
#             "owner_object_id",
#             "owner",
#             "description",
#             "data_schema",
#         ]

#     @extend_schema_field(serializers.DictField(allow_null=True))
#     def get_owner(self, obj):
#         if obj.owner is None:
#             return None
#         serializer = get_serializer_for_model(obj.owner, prefix="Nested")
#         context = {"request": self.context["request"]}
#         return serializer(obj.owner, context=context).data