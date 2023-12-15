from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from nautobot.extras.models import StatusModel
from nautobot.extras.utils import extras_features
from nautobot.core.fields import AutoSlugField
from nautobot.core.models.generics import PrimaryModel

@extras_features(
    'graphql'
)
class ServiceProvider(PrimaryModel):
    name = models.CharField(max_length=255, help_text="Provider Name.")
    slug = AutoSlugField(populate_from="name")
    enable = models.BooleanField(
        default=True,
        help_text="Enables the CDN to deliver content from this service provider, true by default."
    )
    serviceProviderId = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10000)],
        blank=True,
        null=True,
        default=None,
    )
    def __str__(self):
        return self.name or super().__str__()
    
    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:serviceprovider", args=[self.pk])
       
    def validate_unique(self, exclude=None):
        if self.name and hasattr(self, "serviceprovider"):
            if ServiceProvider.objects.exclude(pk=self.pk).filter(name=self.name, site=self.serviceprovider):
                raise ValidationError({"name": "A service provider with this name already exists."})

        super().validate_unique(exclude)

    def clean(self):
        super().clean()

@extras_features(
    'graphql'
)
class ContentProvider(PrimaryModel):
    name = models.CharField(max_length=255, help_text="Provider Name.")
    slug = AutoSlugField(populate_from="name")
    enable = models.BooleanField(
        default=True,
        help_text="Enables the CDN to deliver content from this content provider, true by default."
    )
    contentProviderId = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10000)],
        blank=True,
        null=True,
        default=None,
    )
    serviceProviderId = models.ForeignKey(
        to="ServiceProvider",
        on_delete=models.PROTECT,
        related_name="contentproviders",
        blank=True,
        null=True,
    )
    
    def __str__(self):
        return self.name or super().__str__()
    
    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:contentprovider", args=[self.pk])
       
    def validate_unique(self, exclude=None):
        if self.name and hasattr(self, "contentprovider"):
            if ContentProvider.objects.exclude(pk=self.pk).filter(name=self.name, site=self.contentprovider):
                raise ValidationError({"name": "A content provider with this name already exists."})

        super().validate_unique(exclude)

    def clean(self):
        super().clean()

class Origin(PrimaryModel, StatusModel):
    # General Origin Configs
    name = models.CharField(max_length=255, help_text="Hostname of the origin server.")
    description = models.CharField(
        max_length=255,
        blank=True,
    )
    contentProviderId = models.ForeignKey(
        to="ContentProvider",
        on_delete=models.PROTECT,
        related_name="origins",
        blank=True,
        null=True,
    )
    enable = models.BooleanField(
        default=True,
        help_text="Enables the CDN to deliver content from this origin server, true by default."
    )
    originTimeout = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(300)],
        help_text="In Seconds"
    )
    hostnameOverride = models.CharField(max_length=255, help_text="Shareable Host FQDN")
    resolvableHostnames = models.JSONField(
        encoder=DjangoJSONEncoder,
        null=True,
        blank=True,
    )
    # CDN Configuration of the origin
    dynamicHierarchy = models.JSONField(
        encoder=DjangoJSONEncoder,
        help_text="Configure a HyperCache node that is the endpoint of an origin path (a root HyperCache) to monitor the health of the origin server by sending a GET request for a specific URL.",
        null=True,
        blank=True,
    )
    fastReroute = models.JSONField(
        encoder=DjangoJSONEncoder,
        help_text="Enables a HyperCache node to detect failed or slow connections to a specific origin IP address, or between Sites, and to send a second request to an alternate origin IP (or site) if the first request is delayed. If a successful response is received from either origin IP (or site), the first response is used to fulfill a client's request. The second response, if received, is ignored. If no connection to either destination is established, or if no response is received within the configured origin timeout value, the requests to the origin (or site) are retried four times before a 504 is returned to the client. This method helps ensure rapid recovery in case a temporary network problem results in loss of the initial request or response.",
        null=True,
        blank=True,
    )
    ipAddressTypes = models.JSONField(
        encoder=DjangoJSONEncoder,
        help_text="A list of IP address types, in preference order, that may be used to communicate with this origin server. Choices include IPV4 and IPV6. By default, both IPv6 and IPv4 are enabled, and IPv6 is preferred. Use a commas to seperate the code or range or codes Ex. 'IPV4', 'IPV6'",
        null=True,
        blank=True,
    )
    cacheableErrorResponseCodes = models.JSONField(
        encoder=DjangoJSONEncoder,
        help_text="A list of HTTP status codes that the HPC caches. Each item is either a single code or a range of codes. The following codes are not allowed, either in single code or as part of a range: 200, 203, 206, 300, 301, 410, 416.. Use a commas to seperate the code or range or codes Ex. '400-499', '500'",
        null=True,
        blank=True,
    )
    errorCacheMaxAge = models.IntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(60)],
        help_text="The maximum age used to specify the length of time that an HTTP status code can be cached by the HPC.",
        blank=True,
        null=True,
    )
    storagePartitionId = models.IntegerField(
        validators=[MinValueValidator(1)],
        blank=True,
        null=True,
        help_text="Identifies the storage partition object."
    )
    enableRequestIdExport = models.BooleanField(
        blank=True,
        help_text="Causes the Hypercache to send its internal request ID to the origin server when ingesting content."
    )
    enableAuthenticatedContent = models.BooleanField(
        default=False,
        help_text="Causes the HyperCache to send a HEAD request to the origin server for each client request. If the response is a status code of 2XX, the content is served to the client. Otherwise, the origin's status code is returned. This typically occurs when the origin server authenticates the client request using a cookie, token, or other means."
    )
    enableSiteRedirects = models.BooleanField(
        default=False,
        help_text="Determines whether or not HyperCache redirects a client to a better site based on the rules in the site map. Enabling this to true allows the HyperCache to adhere to the LCDN site map configured using the request router service. If set to false, cache miss client requests to a CDN prefix that uses this origin server as a default result in a HyperCache request for the content directly to the origin server."
    )
    cachingType = models.CharField(
       max_length=32,
       default="OPTIMISTIC",
       choices=[
           ("CONSERVATIVE", "CONSERVATIVE"),
           ("OPTIMISTIC", "OPTIMISTIC"),
           ],
       help_text="Determines whether to validate requests for cached content with the origin server. With default OPTIMISTIC caching, the HyperCache serves cached content without validating the content with the origin server, unless the content is expired. With CONSERVATIVE caching, every cache request is validated with the origin server by sending an HTTP HEAD request. If the content is stale, the HyperCache node gets the new content from the origin server. The old content ages out of the cache."
    )
    interSiteProtocol = models.CharField(
       max_length=32,
       default="HTTP",
       choices=[
           ("HTTP", "HTTP"),
           ("HTTPS", "HTTPS"),
           ],
       help_text="The protocol used to transport this origin's content between Sites in the LCDN, either HTTP or HTTPS."
    )
    intraSiteProtocol = models.CharField(
       max_length=32,
       default="HTTP",
       choices=[
           ("HTTP", "HTTP"),
           ("HTTPS", "HTTPS"),
           ],
       help_text="The protocol used to transport this origin's content between nodes within a site in the LCDN, either HTTP or HTTPS."
    )
    edgeHostType = models.CharField(
       max_length=32,
       default="HTTP",
       choices=[
           ("HTTP", "HTTP"),
           ("AEX", "AEX"),
           ],
       help_text="Indicates whether the origin server is an AEX (Aura Edge eXchange) server, or HTTP, the default."
    )
    edgeHostname = models.CharField(
       max_length=32,
       blank=True,
       help_text="Hostname of the AEX origin server."
    )
    errorCacheMaxRetry = models.IntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(16)],
        help_text="The maximum number of retries in the case of an error response.",
        blank=True,
        null=True,
    )
    
    
    # def __str__(self):
    #     if self.owner:
    #         return f"[{self.owner}] {self.name}"
    #     return self.name

    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:origin", kwargs={"pk": self.pk})
    
    def __str__(self):
        return self.name
    
    def clean(self):
        super().clean()

        # Verify that JSON data is provided as an object
        if self.dynamicHierarchy and not isinstance(self.dynamicHierarchy, dict):
            raise ValidationError({"dynamicHierarchy": 'JSON data must be in object form or blank. Example: {"foo": 123}'})
        if self.fastReroute and not isinstance(self.fastReroute, dict):
            raise ValidationError({"fastReroute": 'JSON data must be in object form or blank. Example: {"foo": 123}'})
        # if self.ipAddressTypes and not isinstance(self.ipAddressTypes, dict):
        #     raise ValidationError({"ipAddressTypes": 'JSON data must be in object form or blank. Example: {"foo": 123}'})
        # if self.cacheableErrorResponseCodes and not isinstance(self.cacheableErrorResponseCodes, dict):
        #     raise ValidationError({"cacheableErrorResponseCodes": 'JSON data must be in object form or blank. Example: {"foo": 123}'})

class CdnPrefix(PrimaryModel, StatusModel):
    name = models.CharField(max_length=255, help_text="The CDN prefix registered on behalf of the content provider. For example, cdn.example.com.")
    contentProviderId = models.ForeignKey(
        to="ContentProvider",
        on_delete=models.PROTECT,
        related_name="cdn_prefixes",
        blank=True,
        null=True,
    )
    cdnPrefixId = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="A unique identifier for the CDN prefix. This should match what is in Akamai AMC.",
        blank=True,
        null=True,
    )
    ipAddressTagId = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Identifies the IP address tag associated with this CDN prefix.",
        blank=True,
        null=True,
    )
    enable = models.BooleanField(
        default=True,
        help_text="Enables the CDN to use this CDN prefix, true by default."
    )
    dnsTtl = models.IntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(2147483647)],
        help_text="DNS response time-to-live (TTL) value for this CDN prefix, in seconds. Note that setting this field is only recommended for CDN operators.",
        blank=True,
        null=True,
    )
    prefixPrioritization = models.CharField(
       max_length=32,
       default="HIGH",
       choices=[
           ("HIGH", "HIGH"),
           ("MEDIUM", "MEDIUM"),
           ("LOW", "LOW"),
           ],
       help_text="Prefix prioritization helps manage peak period resources by prioritizing requests for content from specific content providers. Priorities are LOW, MEDIUM, or HIGH. Default: HIGH"
    )
    keepaliveRequests = models.IntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(100000)],
        help_text="Sets the maximum number of requests that can be served through one keep-alive connection. After the maximum number of requests are made, the connection is closed.",
        blank=True,
        null=True,
    )
    siteMapId = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Identifies the site map associated with this CDN prefix. Note that setting this field is only recommended for CDN operators.",
        blank=True,
        null=True,
    )
    accessMapId = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Identifies the access map associated with this CDN prefix.",
        blank=True,
        null=True,
    )
    
    class Meta:
        verbose_name_plural = "CDN Prefixes"
    
    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:cdnprefix", kwargs={"pk": self.pk})
    
    def __str__(self):
        return self.name
    
class CdnPrefixDefaultBehavior(PrimaryModel, StatusModel):
    name = models.CharField(max_length=255, help_text="Unique name for the set of default behaviors.")
    cdnPrefixId = models.ForeignKey(
        to="CdnPrefix",
        on_delete=models.PROTECT,
        related_name="cdn_prefix_default_behaviors",
        blank=True,
        null=True,
    )
    contentProviderId = models.ForeignKey(
        to="ContentProvider",
        on_delete=models.PROTECT,
        related_name="cdn_prefix_default_behaviors",
        blank=True,
        null=True,
    )
    defaultBehaviors = models.JSONField(
        encoder=DjangoJSONEncoder,
        help_text="A set of features (behaviors) for the top-level (default) rule. These default behaviors are applied to all requests and should be in an Array.",
        null=True,
        blank=True,
    )
    class Meta:
        verbose_name_plural = "CDN Prefix Default Behaviors"
        
    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:cdnprefixdefaultbehavior", kwargs={"pk": self.pk})
    
    def __str__(self):
        return self.name

class CdnPrefixBehavior(PrimaryModel, StatusModel):
    name = models.CharField(max_length=255, help_text="Unique name for the set of behaviors.")
    cdnPrefixId = models.ForeignKey(
        to="CdnPrefix",
        on_delete=models.PROTECT,
        related_name="cdn_prefix_behaviors",
        blank=True,
        null=True,
    )
    contentProviderId = models.ForeignKey(
        to="ContentProvider",
        on_delete=models.PROTECT,
        related_name="cdn_prefix_behaviors",
        blank=True,
        null=True,
    )
    Behaviors = models.JSONField(
        encoder=DjangoJSONEncoder,
        help_text="A set of features (behaviors) for the top-level (default) rule. These default behaviors are applied to all requests and should be in an Array.",
        null=True,
        blank=True,
    )
    
    class Meta:
        verbose_name_plural = "CDN Prefix Behaviors"
        
    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:cdnprefixbehavior", kwargs={"pk": self.pk})
    
    def __str__(self):
        return self.name
