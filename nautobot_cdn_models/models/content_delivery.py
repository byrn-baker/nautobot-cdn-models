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
        related_name="serviceproviderid",
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
        related_name="contentproviderid",
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
    resolvableHostnames = ArrayField(
        ArrayField(
            models.CharField(max_length=10, blank=True),
            size=10,
        ),
        size=10,
        null=True,
        blank=True,
    )
    # CDN Configuration of the origin
    dynamicHierarchy = models.JSONField(
        encoder=DjangoJSONEncoder,
        help_text="Configure a HyperCache node that is the endpoint of an origin path (a root HyperCache) to monitor the health of the origin server by sending a GET request for a specific URL."
    )
    fastReroute = models.JSONField(
        encoder=DjangoJSONEncoder,
        help_text="Enables a HyperCache node to detect failed or slow connections to a specific origin IP address, or between Sites, and to send a second request to an alternate origin IP (or site) if the first request is delayed. If a successful response is received from either origin IP (or site), the first response is used to fulfill a client's request. The second response, if received, is ignored. If no connection to either destination is established, or if no response is received within the configured origin timeout value, the requests to the origin (or site) are retried four times before a 504 is returned to the client. This method helps ensure rapid recovery in case a temporary network problem results in loss of the initial request or response."
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
    ipAddressTypes = ArrayField(
        ArrayField(
            models.CharField(max_length=4, blank=True),
            size=6,
        ),
        size=6,
        null=True,
        blank=True,
    )
    cacheableErrorResponseCodes = ArrayField(
        ArrayField(
            models.CharField(max_length=10, blank=True),
            size=10,
        ),
        size=10,
        default=list,
        null=True,
        blank=True,
    )
    errorCacheMaxAge = models.IntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(60)],
        blank=True,
        null=True,
        help_text="The maximum age used to specify the length of time that an HTTP status code can be cached by the HPC."
    )
    errorCacheMaxRetry = models.IntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(16)],
        blank=True,
        null=True,
        help_text="The maximum number of retries in the case of an error response."
    )
    
    
    # def __str__(self):
    #     if self.owner:
    #         return f"[{self.owner}] {self.name}"
    #     return self.name

    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:origin", kwargs={"pk": self.pk})
    
    def clean(self):
        super().clean()

        # Verify that JSON data is provided as an object
        if not isinstance(self.dynamicHierarchy, dict):
            raise ValidationError({"data": 'JSON data must be in object form. Example: {"foo": 123}'})
        if not isinstance(self.fastReroute, dict):
            raise ValidationError({"data": 'JSON data must be in object form. Example: {"foo": 123}'})