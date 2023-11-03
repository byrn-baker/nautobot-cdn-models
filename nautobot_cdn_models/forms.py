from django import forms

from nautobot.core.forms import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    CSVContentTypeField,
)
from nautobot.extras.forms import (
    CustomFieldModelCSVForm,
    NautobotFilterForm,
    NautobotBulkEditForm,
    NautobotModelForm,
    TagsBulkEditFormMixin,
)
from nautobot.dcim.models import Location
from nautobot.extras.models import Status
from .models import CdnSite, SiteRole, HyperCacheMemoryProfile


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

# class CdnSiteCSVForm(CustomFieldModelCSVForm):
#     location = CSVContentTypeField(
#         queryset=Location.objects.all(),
#         required=False,
#         to_field_name="name",
#         help_text="Assigned location",
#     )
#     cdn_site_role = CSVContentTypeField(
#         queryset=SiteRole.objects.all(),
#         required=False,
#         to_field_name="name",
#         help_text="Assigned tenant",
#     )

#     class Meta:
#         model = CdnSite
#         fields = CdnSite.csv_headers


#
# Form extensions
#


# class CdnSiteForm(forms.Form):
#     cdn_site_role = DynamicModelChoiceField(
#         queryset=SiteRole.objects.all(),
#         required=False,
#         null_option="None",
#         initial_params={"cdnsites": "$cdnsite"},
#     )
#     cdnsite = DynamicModelChoiceField(
#         queryset=CdnSite.objects.all(),
#         required=False,
#         query_params={"cdn_site_role": "$cdn_site_role"},
#     )


# class CdnSiteFilterForm(forms.Form):
#     cdn_site_role = DynamicModelMultipleChoiceField(
#         queryset=SiteRole.objects.all(),
#         to_field_name="name",
#         required=False,
#         null_option="None",
#     )
#     cdnsite = DynamicModelMultipleChoiceField(
#         queryset=CdnSite.objects.all(),
#         to_field_name="name",
#         required=False,
#         null_option="None",
#         query_params={"cdn_site_role": "$cdn_site_role"},
#     )