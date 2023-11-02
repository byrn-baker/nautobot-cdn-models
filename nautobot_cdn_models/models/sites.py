from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey

from nautobot.extras.models import StatusModel
from nautobot.extras.utils import extras_features
from nautobot.core.fields import AutoSlugField
from nautobot.core.models.generics import OrganizationalModel, PrimaryModel
from nautobot.utilities.fields import NaturalOrderingField
from nautobot.utilities.mptt import TreeManager

from .contexts import CdnConfigContextModel
from ..querysets import CdnConfigContextModelQuerySet

@extras_features(
    'graphql'
)
class HyperCacheMemoryProfile(PrimaryModel):
    name = models.CharField(max_length=255, help_text="Profile Name.")
    slug = AutoSlugField(populate_from="name")
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
   
    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:hypercachememoryprofile", args=[self.slug])
    
    def __str__(self):
        return self.name

@extras_features(
    'graphql'
)
class SiteRole(MPTTModel, OrganizationalModel):
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from="name")
    parent = TreeForeignKey(
        to="self",
        on_delete=models.CASCADE,
        related_name="children",
        blank=True,
        null=True,
        db_index=True,
    )
    description = models.CharField(max_length=200, blank=True)

    objects = TreeManager()

    csv_headers = ["name", "slug", "parent", "description"]

    class Meta:
        ordering = ["name"]

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:siterole", args=[self.slug])
    
    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.parent.name if self.parent else "",
            self.description,
        )
    
    def to_objectchange(self, action, object_data_exclude=None, **kwargs):
        if object_data_exclude is None:
            object_data_exclude = []
        # Remove MPTT-internal fields
        object_data_exclude += ["level", "lft", "rght", "tree_id"]
        return super().to_objectchange(action, object_data_exclude=object_data_exclude, **kwargs)

@extras_features(
    'statuses',
    'relationships',
    'graphql'
)
class CdnSite(PrimaryModel, CdnConfigContextModel, StatusModel):
    name = models.CharField(max_length=255, help_text="Akamai Site Name.")
    _name = NaturalOrderingField(target_field="name", max_length=100, blank=True, db_index=True)
    cdn_site_role = models.ForeignKey(
        to="SiteRole",
        on_delete=models.SET_NULL,
        related_name="cdnsites",
        blank=True,
        null=True,
    )
    region = models.ForeignKey(
        to="dcim.Region",
        on_delete=models.SET_NULL,
        related_name="cdnsites",
        blank=True,
        null=True,
    )
    site = models.ForeignKey(
        to="dcim.Site",
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

    objects = CdnConfigContextModelQuerySet.as_manager()

    csv_headers = [
        "name",
        "status",
        "region",
        "site",
        "cdn_site_role",
        "abbreviatedName",
        "bandwidthLimitMbps",
        "enableDisklessMode",
        "neighbor1",
        "neighbor1_preference",
        "neighbor2",
        "neighbor2_preference",
        "cacheMemoryProfileId",
        "siteId",

    ]
    clone_fields = [
        "status",
        "region",
        "abbreviatedName",
        "bandwidthLimitMbps",
        "enableDisklessMode",
        "neighbor1",
        "neighbor1_preference",
        "neighbor2",
        "neighbor2_preference",
        "cacheMemoryProfileId",
        "siteId",
    ]

    class Meta:
        ordering = ["cdn_site_role", "_name"]
        unique_together = (
            ("cdn_site_role", "region", "name"),  # See validate_unique below
        )
    
    def __str__(self):
        return self.name or super().__str__()
    
    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:cdnsite", args=[self.pk])
       
    def validate_unique(self, exclude=None):
        if self.name and hasattr(self, "cdnsite") and self.region is None:
            if CdnSite.objects.exclude(pk=self.pk).filter(name=self.name, site=self.cdnsite, region__isnull=True):
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
            self.status,
            self.region,
            self.site,
            self.siteId,
        )
    