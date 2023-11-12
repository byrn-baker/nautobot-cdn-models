from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

from nautobot.core.models.generics import OrganizationalModel, PrimaryModel
from nautobot.core.models.tree_queries import TreeModel
from nautobot.extras.utils import extras_features
from nautobot.extras.models import StatusField, Tag

from ..querysets import RedirectMapContextModelQuerySet
from .redirectmap import RedirectMapContextModel

__all__ = (
    "CdnSite",
    "SiteRole",
    "HyperCacheMemoryProfile"
)

@extras_features(
    'graphql'
)
class HyperCacheMemoryProfile(PrimaryModel):
    name = models.CharField(max_length=100, help_text="Profile Name.")
    description = models.CharField(max_length=255, blank=True, help_text="A description of the Memory profile.")
    frontEndCacheMemoryPercent = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    ramOnlyCacheMemoryPercent = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    hotCacheMemoryPercent = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    diskIndexMemoryPercent = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    cacheMemoryProfileId = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10000)],
    )
   
    class Meta:
        ordering = ["name"]
        unique_together = (
            ("name"),  # See validate_unique below
        )
        
    def validate_unique(self, exclude=None):
        if self.name and hasattr(self, "name"):
            if CdnSite.objects.exclude(pk=self.pk).filter(name=self.name):
                raise ValidationError({"name": "A profile with this name already exists."})

        super().validate_unique(exclude)
    
    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:hypercachememoryprofile", args=[self.pk])
    
    def __str__(self):
        return self.name
    

@extras_features(
    "custom_validators",
    "graphql",
)
class SiteRole(TreeModel, OrganizationalModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:siterole", args=[self.pk])


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "webhooks",
)
class CdnSite(PrimaryModel, RedirectMapContextModel):
    name = models.CharField(max_length=100, help_text="Akamai Site Name.")
    cdn_site_role = models.ForeignKey(
        to="SiteRole",
        on_delete=models.SET_NULL,
        related_name="cdnsites",
        blank=True,
        null=True,
    )
    location = models.ForeignKey(
        to="dcim.Location",
        on_delete=models.PROTECT,
        related_name="cdnsites",
        blank=True,
        null=True,
    )
    status = StatusField(
        blank=False, 
        null=True,
    )
    abbreviatedName = models.CharField(max_length=255, blank=True, help_text="Akamai Site Name Abbreviation")
    bandwidthLimitMbps = models.IntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(10000000)],
        blank=True,
        null=True,
    )
    enableDisklessMode = models.BooleanField(
        default=False,
        help_text="Enables Diskless Mode for the site, False by default.",
    )
    neighbor1 = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_neighbor",
        help_text="Only required for HPC sites, this defines the primary neighbor"
    )
    neighbor1_preference = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10000)],
        blank=True,
        null=True,
        default=1000
    )
    neighbor2 = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="secondary_neighbor",
        help_text="Only Required for HPC sites, this defines the secondary neighbor",
    )
    neighbor2_preference = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10000)],
        blank=True,
        null=True,
        default=750
    )
    failover_site = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sister_site",
        help_text="Select the site to which this site will failover to."
    )
    cacheMemoryProfileId = models.ForeignKey(
        to="HyperCacheMemoryProfile",
        on_delete=models.PROTECT,
        related_name="CacheMemoryProfileId",
        blank=True,
        null=True,
    )
    siteId = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10000)],
        blank=True,
        null=True,
        default=None,
    )
    tags = models.ManyToManyField(to="extras.Tag", related_name="+", blank=True)

    objects = RedirectMapContextModelQuerySet.as_manager()

    csv_headers = [
        "name",
        "status",
        "location",
        "site",
        "cdn_site_role",
        "abbreviatedName",
        "bandwidthLimitMbps",
        "enableDisklessMode",
        "neighbor1",
        "neighbor1_preference",
        "neighbor2",
        "neighbor2_preference",
        "failover_site",
        "cacheMemoryProfileId",
        "siteId",

    ]
    clone_fields = [
        "status",
        "location",
        "abbreviatedName",
        "bandwidthLimitMbps",
        "enableDisklessMode",
        "neighbor1",
        "neighbor1_preference",
        "neighbor2",
        "neighbor2_preference",
        "failover_site",
        "cacheMemoryProfileId",
        "siteId",
    ]

    class Meta:
        ordering = ["cdn_site_role", "name"]
        unique_together = (
            ("cdn_site_role", "location", "name"),  # See validate_unique below
        )
    
    def __str__(self):
        return self.name or super().__str__()
    
    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:cdnsite", args=[self.pk])
       
    def validate_unique(self, exclude=None):
        if self.name and hasattr(self, "cdnsite") and self.location is None:
            if CdnSite.objects.exclude(pk=self.pk).filter(name=self.name, location=self.cdnsite):
                raise ValidationError({"name": "A cdnsite with this name already exists."})

        super().validate_unique(exclude)

    def clean(self):
        super().clean()

    
    def to_csv(self):
        return (
            self.name,
            self.cdn_site_role.name if self.cdn_site_role else None,
            self.abbreviatedName,
            self.enableDisklessMode,
            self.bandwidthLimitMbps,
            self.neighbor1,
            self.neighbor1_preference,
            self.neighbor2,
            self.neighbor2_preference,
            self.cacheMemoryProfileId,
            self.failover_site,
            self.status,
            self.siteId,
        )