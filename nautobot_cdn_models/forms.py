import json
from django import forms
from django.core.exceptions import ValidationError

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

### This class is for the array fields being used instead of json fields.
class ArrayField(forms.Field):
    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        try:
            return [item.strip() for item in value.split(',')]
        except (ValueError, TypeError):
            raise exceptions.ValidationError('Invalid input for array field')
        
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
    region = DynamicModelChoiceField(required=False, queryset=Region.objects.all())
    site = DynamicModelChoiceField(required=False, queryset=Site.objects.all())
    cdn_site_role = forms.ModelChoiceField(required=False, queryset=models.SiteRole.objects.all())
    neighbor1 = DynamicModelChoiceField(required=False, queryset=models.CdnSite.objects.all(), label="Primary Site Neighbor")
    neighbor2 = DynamicModelChoiceField(required=False, queryset=models.CdnSite.objects.all(), label="Secondary Site Neighbor")
    hyperCacheMemoryProfileId = DynamicModelChoiceField(required=False, queryset=models.HyperCacheMemoryProfile.objects.all(), label="Akamai Site Memory Profile ID")
    failover_site = DynamicModelChoiceField(required=False, queryset=models.CdnSite.objects.all(), label="Failover Site")
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
            'failover_site',
            'hyperCacheMemoryProfileId',
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
    hyperCacheMemoryProfileId = DynamicModelChoiceField(required=False, queryset=models.HyperCacheMemoryProfile.objects.all(), label="Akamai Site Memory Profile ID")
    neighbor1 = DynamicModelChoiceField(required=False, queryset=models.CdnSite.objects.all(), label="Primary Site Neighbor")
    neighbor2 = DynamicModelChoiceField(required=False, queryset=models.CdnSite.objects.all(), label="Secondary Site Neighbor")
    cdn_site_role = DynamicModelMultipleChoiceField(required=False, queryset=models.SiteRole.objects.all())

class CdnSiteBulkEditForm(StatusModelBulkEditFormMixin, NautobotBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=models.CdnSite.objects.all(), widget=forms.MultipleHiddenInput)
    region = DynamicModelChoiceField(queryset=Region.objects.all(), required=False)
    cdn_site_role = DynamicModelChoiceField(queryset=models.SiteRole.objects.all(), required=False)
    bandwidthLimitMbps = forms.IntegerField(required=False, label="Site Bandwidth Limit")
    enableDisklessMode = forms.BooleanField(required=False, label="Site Disk Mode")
    hyperCacheMemoryProfileId = forms.ModelChoiceField(required=False, queryset=models.HyperCacheMemoryProfile.objects.all(), label="Akamai Site Memory Profile ID")
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
    failover_site = DynamicModelChoiceField(queryset=models.CdnSite.objects.all(), required=False)
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
            "failover_site",
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


#
# Content Delivery
#

class ServiceProviderForm(NautobotModelForm):
    slug = SlugField(label="account")

    class Meta:
        model = models.ServiceProvider
        fields = [
            'name',
            'slug',
            'enable',
            'serviceProviderId',
        ]

class ServiceProviderFilterForm(NautobotFilterForm):
    model = models.ServiceProvider

    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)

class ContentProviderForm(NautobotModelForm):
    slug = SlugField(label="account")

    class Meta:
        model = models.ContentProvider
        fields = [
            'name',
            'slug',
            'enable',
            'contentProviderId',
            'serviceProviderId',
        ]

class ContentProviderFilterForm(NautobotFilterForm):
    model = models.ContentProvider

    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)

class OriginForm(NautobotModelForm):
    contentProviderId = DynamicModelChoiceField(queryset=models.ContentProvider.objects.all(), required=False)
    resolvableHostnames = ArrayField(
        label="Shareable Host FQDN", 
        help_text="A list of virtual hosts, origin servers with resolvable hostnames. These resolvable hostnames are used by DNS to determine the IP addresses of the destination origin server.",
        widget=forms.Textarea,
        required=False
    )
    dynamicHierarchy = JSONField(
        label="Origin Health Check",
        help_text="Configure a HyperCache node that is the endpoint of an origin path (a root HyperCache) to monitor the health of the origin server by sending a GET request for a specific URL."
    )
    fastReroute = JSONField(
        label="Fast ReRoute",
        help_text="Enables a HyperCache node to detect failed or slow connections to a specific origin IP address, or between Sites, and to send a second request to an alternate origin IP (or site) if the first request is delayed. If a successful response is received from either origin IP (or site), the first response is used to fulfill a client's request. The second response, if received, is ignored. If no connection to either destination is established, or if no response is received within the configured origin timeout value, the requests to the origin (or site) are retried four times before a 504 is returned to the client. This method helps ensure rapid recovery in case a temporary network problem results in loss of the initial request or response."
    )
    ipAddressTypes = ArrayField(
        label="IP Address Types", 
        help_text="A list of IP address types, in preference order, that may be used to communicate with this origin server. Choices include IPV4 and IPV6. By default, both IPv6 and IPv4 are enabled, and IPv6 is preferred. Use a commas to seperate the code or range or codes Ex. 'IPV4', 'IPV6'",
        widget=forms.Textarea,
        required=False
    )
    cacheableErrorResponseCodes = ArrayField(
        label="HTTP Status Codes", 
        help_text="A list of HTTP status codes that the HPC caches. Each item is either a single code or a range of codes. The following codes are not allowed, either in single code or as part of a range: 200, 203, 206, 300, 301, 410, 416.. Use a commas to seperate the code or range or codes Ex. '400-499', '500'",
        widget=forms.Textarea,
        required=False
    )
    errorCacheMaxRetry = forms.IntegerField(label="Max Retry", help_text="The maximum number of retries in the case of an error response.")
    errorCacheMaxAge = forms.IntegerField(label="Max Age (s)",help_text="The maximum age used to specify the length of time that an HTTP status code can be cached by the HPC.")
    
    def clean_dynamicHierarchy(self):
        data = self.cleaned_data['dynamicHierarchy']
        if isinstance(data, str):
            try:
                # Try to parse the string into a JSON object
                json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON data for dynamicHierarchy field")
        return data

    def clean_fastReroute(self):
        data = self.cleaned_data['fastReroute']
        if isinstance(data, str):
            try:
                # Try to parse the string into a JSON object
                json.loads(data)
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON data for fastReroute field")
        return data
    
    class Meta:
        model = models.Origin
        fields = (
            'name',
            'description',
            'contentProviderId',
            'enable',
            'originTimeout',
            'hostnameOverride',
            'resolvableHostnames',
            'dynamicHierarchy',
            'fastReroute',
            'storagePartitionId',
            'cacheableErrorResponseCodes',
            'enableRequestIdExport',
            'errorCacheMaxAge',
            'errorCacheMaxRetry',
            'enableAuthenticatedContent',
            'enableSiteRedirects',
            'cachingType',
            'interSiteProtocol',
            'intraSiteProtocol',
            'edgeHostType',
            'edgeHostname',
            'ipAddressTypes',
        )

class OriginFilterForm(NautobotFilterForm):
    model = models.Origin

    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)