from django import forms

from nautobot.extras.forms import (
    CustomFieldModelCSVForm,
    NautobotBulkEditForm,
    NautobotModelForm,
    NautobotFilterForm,
    StatusModelBulkEditFormMixin,
    StatusModelCSVFormMixin,
    StatusModelFilterFormMixin,
    LocalContextFilterForm,
    LocalContextModelForm,
)
from nautobot.utilities.forms import (
    BootstrapMixin,
    BulkEditForm,
    BulkEditNullBooleanSelect,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    JSONField,
    SlugField,
)
from nautobot.extras.forms.mixins import (
    NoteModelBulkEditFormMixin,
    NoteModelFormMixin,
)
from nautobot.extras.models import Tag
from nautobot.dcim.models import Region, Site
from nautobot.extras.models import ConfigContextSchema
from . import models

class HyperCacheMemoryProfileForm(NautobotModelForm):
    slug = SlugField()

    class Meta:
        model = models.HyperCacheMemoryProfile
        fields = [
            'name',
            'slug',
            'description',
            'hotCacheMemoryPercent',
            'ramOnlyCacheMemoryPercent',
            'diskIndexMemoryPercent',
            'frontEndCacheMemoryPercent',
            'cacheMemoryProfileId',
        ]

class HyperCacheMemoryProfileFilterForm(NautobotFilterForm):
    model = models.HyperCacheMemoryProfile

    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)

class SiteRoleForm(NautobotModelForm):
    parent = DynamicModelChoiceField(queryset=models.SiteRole.objects.all(), required=False)
    slug = SlugField()

    class Meta:
        model = models.SiteRole
        fields = [
            "parent",
            "name",
            "slug",
            "description",
        ]

class SiteRoleFilterForm(NautobotFilterForm):
    model = models.SiteRole

    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)

class SiteRoleCSVForm(CustomFieldModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=models.SiteRole.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Parent role",
    )

    class Meta:
        model = models.SiteRole
        fields = models.SiteRole.csv_headers


class CdnSiteForm(NautobotModelForm, LocalContextModelForm):
    region = DynamicModelChoiceField(queryset=Region.objects.all(), required=False)
    site = DynamicModelChoiceField(queryset=Site.objects.all(), required=False)
    cdn_site_role = forms.ModelChoiceField(queryset=models.SiteRole.objects.all(), required=False,)
    cacheMemoryProfileId = DynamicModelChoiceField(required=False, queryset=models.HyperCacheMemoryProfile.objects.all())
    class Meta:
        model = models.CdnSite
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
            'region',
            'site',
            'local_context_data',
            'local_context_schema',
        ]

class CdnSiteFilterForm(NautobotFilterForm, StatusModelFilterFormMixin, LocalContextFilterForm):
    model = models.CdnSite

    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)
    bandwidthLimitMbps = forms.IntegerField(required=False, label="Site Bandwidth Limit")
    enableDisklessMode = forms.BooleanField(required=False, label="Site Disk Mode")
    cacheMemoryProfileId = DynamicModelChoiceField(required=False, queryset=models.HyperCacheMemoryProfile.objects.all(), label="Akamai Site Memory Profile ID")
    neighbor1 = DynamicModelChoiceField(required=False, queryset=models.CdnSite.objects.all(), label="Primary Site Neighbor")
    neighbor2 = DynamicModelChoiceField(required=False, queryset=models.CdnSite.objects.all(), label="Secondary Site Neighbor")
    cdn_site_role = DynamicModelMultipleChoiceField(required=False, queryset=models.SiteRole.objects.all())

class CdnSiteBulkEditForm(StatusModelBulkEditFormMixin, NautobotBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=models.CdnSite.objects.all(), widget=forms.MultipleHiddenInput)
    region = DynamicModelChoiceField(queryset=Region.objects.all(), required=False)
    cdn_site_role = DynamicModelChoiceField(queryset=models.SiteRole.objects.all(), required=False)
    bandwidthLimitMbps = forms.IntegerField(required=False, label="Site Bandwidth Limit")
    enableDisklessMode = forms.BooleanField(required=False, label="Site Disk Mode")
    cacheMemoryProfileId = forms.ModelChoiceField(required=False, queryset=models.HyperCacheMemoryProfile.objects.all(), label="Akamai Site Memory Profile ID")
    neighbor1 = DynamicModelChoiceField(required=False, queryset=models.CdnSite.objects.all(), label="Primary Site Neighbor")
    neighbor1_preference = forms.IntegerField(required=False, label="Neighbor Preference")
    neighbor2 = DynamicModelChoiceField(required=False, queryset=models.CdnSite.objects.all(), label="Secondary Site Neighbor")
    neighbor2_preference = forms.IntegerField(required=False, label="Neighbor Preference")

    class Meta:
        nullable_fields = [
            "region",
            "cdn_site_role",
            "cacheMemoryProfileId",
            "enableDisklessMode",
            "neighbor1",
            "neighbor2",
        ]

class CdnSiteCSVForm(StatusModelCSVFormMixin, CustomFieldModelCSVForm):
    region = CSVModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Assigned region",
    )
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Assigned site",
    )
    cdn_site_role = CSVModelChoiceField(
        queryset=models.SiteRole.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Assigned tenant",
    )

    class Meta:
        model = models.CdnSite
        fields = models.CdnSite.csv_headers

class CdnConfigContextForm(BootstrapMixin, NoteModelFormMixin, forms.ModelForm):
    regions = DynamicModelMultipleChoiceField(queryset=Region.objects.all(), required=False)
    cdnsites = DynamicModelMultipleChoiceField(queryset=models.CdnSite.objects.all(), required=False)
    cdn_site_roles = DynamicModelMultipleChoiceField(queryset=models.SiteRole.objects.all(), required=False)
    tag = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), to_field_name="slug", required=False)
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    data = JSONField(label="")

    class Meta:
        model = models.CdnConfigContext
        fields = (
            "name",
            "weight",
            "description",
            "schema",
            "is_active",
            "regions",
            "cdnsites",
            "cdn_site_roles",
            "tags",
            "data",
        )


class CdnConfigContextBulkEditForm(BootstrapMixin, NoteModelBulkEditFormMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=models.CdnConfigContext.objects.all(), widget=forms.MultipleHiddenInput)
    schema = DynamicModelChoiceField(queryset=ConfigContextSchema.objects.all(), required=False)
    weight = forms.IntegerField(required=False, min_value=0)
    is_active = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect())
    description = forms.CharField(required=False, max_length=100)

    class Meta:
        nullable_fields = [
            "description",
            "schema",
        ]


class CdnConfigContextFilterForm(BootstrapMixin, forms.Form):
    q = forms.CharField(required=False, label="Search")
    schema = DynamicModelChoiceField(queryset=ConfigContextSchema.objects.all(), to_field_name="slug", required=False)
    region = DynamicModelMultipleChoiceField(queryset=Region.objects.all(), to_field_name="slug", required=False)
    cdnsite = DynamicModelMultipleChoiceField(queryset=models.CdnSite.objects.all(), to_field_name="slug", required=False)
    cdn_site_roles = DynamicModelMultipleChoiceField(queryset=models.SiteRole.objects.all(), to_field_name="slug", required=False)
    tag = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), to_field_name="slug", required=False)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)


#
# Config context schemas
#


# class CdnConfigContextSchemaForm(NautobotModelForm):
#     data_schema = JSONField(label="")
#     slug = SlugField()

#     class Meta:
#         model = models.CdnConfigContextSchema
#         fields = (
#             "name",
#             "slug",
#             "description",
#             "data_schema",
#         )


# class CdnConfigContextSchemaBulkEditForm(NautobotBulkEditForm):
#     pk = forms.ModelMultipleChoiceField(queryset=models.CdnConfigContextSchema.objects.all(), widget=forms.MultipleHiddenInput)
#     description = forms.CharField(required=False, max_length=100)

#     class Meta:
#         nullable_fields = [
#             "description",
#         ]


# class CdnConfigContextSchemaFilterForm(BootstrapMixin, forms.Form):
#     q = forms.CharField(required=False, label="Search")