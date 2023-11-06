from django import forms

from nautobot.core.forms import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    CSVContentTypeField,
)
from nautobot.core.forms import (
    BootstrapMixin,
    BulkEditForm,
    BulkEditNullBooleanSelect,
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    JSONField,
)
from nautobot.extras.forms import (
    NautobotBulkEditForm,
    NautobotModelForm,
    NautobotFilterForm,
)
from nautobot.extras.forms.mixins import (
    NoteModelBulkEditFormMixin,
    NoteModelFormMixin,
)
from nautobot.dcim.models import Location
from nautobot.extras.models import Status, Tag
from nautobot.extras.models import ConfigContextSchema
from .models import CdnSite, SiteRole, HyperCacheMemoryProfile, RedirectMapContext


class HyperCacheMemoryProfileForm(NautobotModelForm):
    class Meta:
        model = HyperCacheMemoryProfile
        fields = [
            'name',
            'description',
            'hotCacheMemoryPercent',
            'ramOnlyCacheMemoryPercent',
            'diskIndexMemoryPercent',
            'frontEndCacheMemoryPercent',
            'cacheMemoryProfileId',
        ]

class HyperCacheMemoryProfileFilterForm(NautobotFilterForm):
    model = HyperCacheMemoryProfile

    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)

#
# Site Roles
#


class SiteRoleForm(NautobotModelForm):
    parent = DynamicModelChoiceField(queryset=SiteRole.objects.all(), required=False)

    class Meta:
        model = SiteRole
        fields = [
            "parent",
            "name",
            "description",
        ]


#
# CDN Sites
#


class CdnSiteForm(NautobotModelForm):
    cdn_site_role = DynamicModelChoiceField(queryset=SiteRole.objects.all(), required=False)
    status = forms.ModelChoiceField(queryset=Status.objects.all(), required=False)
    comments = CommentField()

    class Meta:
        model = CdnSite
        fields = [
            'name',
            "status",
            'abbreviatedName',
            'bandwidthLimitMbps',
            'enableDisklessMode',
            'neighbor1',
            'neighbor1_preference',
            'neighbor2',
            'neighbor2_preference',
            'cacheMemoryProfileId',
            'siteId',
            'cdn_site_role',
            'location',
        ]


class CdnSiteBulkEditForm(NautobotBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=CdnSite.objects.all(), widget=forms.MultipleHiddenInput)
    status = forms.ModelChoiceField(queryset=Status.objects.all(), required=False)
    location = DynamicModelChoiceField(queryset=Location.objects.all(), required=False)
    cdn_site_role = DynamicModelChoiceField(queryset=SiteRole.objects.all(), required=False)
    bandwidthLimitMbps = forms.IntegerField(required=False, label="Site Bandwidth Limit")
    enableDisklessMode = forms.BooleanField(required=False, label="Site Disk Mode")
    cacheMemoryProfileId = forms.ModelChoiceField(required=False, queryset=HyperCacheMemoryProfile.objects.all(), label="Akamai Site Memory Profile ID")
    neighbor1 = DynamicModelChoiceField(required=False, queryset=CdnSite.objects.all(), label="Primary Site Neighbor")
    neighbor1_preference = forms.IntegerField(required=False, label="Neighbor Preference")
    neighbor2 = DynamicModelChoiceField(required=False, queryset=CdnSite.objects.all(), label="Secondary Site Neighbor")
    neighbor2_preference = forms.IntegerField(required=False, label="Neighbor Preference")

    class Meta:
        nullable_fields = [
            "location",
            "cdn_site_role",
            "cacheMemoryProfileId",
            "enableDisklessMode",
            "neighbor1",
            "neighbor2",
        ]



class CdnSiteFilterForm(NautobotFilterForm):
    model = CdnSite

    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)
    bandwidthLimitMbps = forms.IntegerField(required=False, label="Site Bandwidth Limit")
    enableDisklessMode = forms.BooleanField(required=False, label="Site Disk Mode")
    cacheMemoryProfileId = DynamicModelChoiceField(required=False, queryset=HyperCacheMemoryProfile.objects.all(), label="Akamai Site Memory Profile ID")
    neighbor1 = DynamicModelChoiceField(required=False, queryset=CdnSite.objects.all(), label="Primary Site Neighbor")
    neighbor2 = DynamicModelChoiceField(required=False, queryset=CdnSite.objects.all(), label="Secondary Site Neighbor")
    cdn_site_role = DynamicModelMultipleChoiceField(required=False, queryset=SiteRole.objects.all())

class RedirectMapContextForm(BootstrapMixin, NoteModelFormMixin):
    locations = DynamicModelMultipleChoiceField(queryset=Location.objects.all(), required=False)
    cdnsites = DynamicModelMultipleChoiceField(queryset=CdnSite.objects.all(), required=False)
    cdn_site_roles = DynamicModelMultipleChoiceField(queryset=SiteRole.objects.all(), required=False)
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    data = JSONField(label="")

    class Meta:
        model = RedirectMapContext
        fields = "__all__"


class RedirectMapContextBulkEditForm(BootstrapMixin, NoteModelBulkEditFormMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=RedirectMapContext.objects.all(), widget=forms.MultipleHiddenInput)
    schema = DynamicModelChoiceField(queryset=ConfigContextSchema.objects.all(), required=False)
    weight = forms.IntegerField(required=False, min_value=0)
    is_active = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect())
    description = forms.CharField(required=False, max_length=100)

    class Meta:
        nullable_fields = [
            "description",
            "schema",
        ]


class RedirectMapContextFilterForm(BootstrapMixin, forms.Form):
    q = forms.CharField(required=False, label="Search")
    schema = DynamicModelChoiceField(queryset=ConfigContextSchema.objects.all(), to_field_name="slug", required=False)
    Location = DynamicModelMultipleChoiceField(queryset=Location.objects.all(), to_field_name="slug", required=False)
    cdnsite = DynamicModelMultipleChoiceField(queryset=CdnSite.objects.all(), to_field_name="slug", required=False)
    cdn_site_roles = DynamicModelMultipleChoiceField(queryset=SiteRole.objects.all(), to_field_name="slug", required=False)
    tag = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), to_field_name="slug", required=False)