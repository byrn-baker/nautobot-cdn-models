from collections import OrderedDict

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from jsonschema import draft7_format_checker
from jsonschema.exceptions import SchemaError, ValidationError as JSONSchemaValidationError
from jsonschema.validators import Draft7Validator

from nautobot.core.fields import AutoSlugField
from nautobot.core.models import BaseModel
from nautobot.core.models.generics import OrganizationalModel

from nautobot.extras.models.models import ChangeLoggedModel, ConfigContextSchemaValidationMixin
from nautobot.extras.models.mixins import NotesMixin
from nautobot.extras.utils import extras_features, FeatureQuery
from nautobot.utilities.utils import deepmerge

from ..querysets import CdnConfigContextQuerySet

# class CdnConfigContextSchemaValidationMixin:
#     """
#     Mixin that provides validation of config context data against a json schema.
#     """

#     def _validate_with_schema(self, data_field, schema_field):
#         schema = getattr(self, schema_field)
#         data = getattr(self, data_field)

#         # If schema is None, then no schema has been specified on the instance and thus no validation should occur.
#         if schema:
#             try:
#                 Draft7Validator(schema.data_schema, format_checker=draft7_format_checker).validate(data)
#             except JSONSchemaValidationError as e:
#                 raise ValidationError({data_field: [f"Validation using the JSON Schema {schema} failed.", e.message]})


@extras_features("graphql")
class CdnConfigContext(BaseModel, ChangeLoggedModel, ConfigContextSchemaValidationMixin, NotesMixin):
    """
    A ConfigContext represents a set of arbitrary data available to any Device or VirtualMachine matching its assigned
    qualifiers (region, site, etc.). For example, the data stored in a ConfigContext assigned to site A and tenant B
    will be available to a Device in site A assigned to tenant B. Data is stored in JSON format.
    """

    name = models.CharField(max_length=100, db_index=True)

    # A ConfigContext *may* be owned by another model, such as a GitRepository, or it may be un-owned
    owner_content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=FeatureQuery("config_context_owners"),
        default=None,
        null=True,
        blank=True,
    )
    owner_object_id = models.UUIDField(default=None, null=True, blank=True)
    owner = GenericForeignKey(
        ct_field="owner_content_type",
        fk_field="owner_object_id",
    )

    weight = models.PositiveSmallIntegerField(default=1000)
    description = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(
        default=True,
    )
    schema = models.ForeignKey(
        to="extras.ConfigContextSchema",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional schema to validate the structure of the data",
    )
    regions = models.ManyToManyField(to="dcim.Region", related_name="+", blank=True)
    cdnsites = models.ManyToManyField(to="CdnSite", related_name="+", blank=True)
    locations = models.ManyToManyField(to="dcim.Location", related_name="+", blank=True)
    cdn_site_roles = models.ManyToManyField(to="SiteRole", related_name="+", blank=True)
    tags = models.ManyToManyField(to="extras.Tag", related_name="+", blank=True)

    data = models.JSONField(encoder=DjangoJSONEncoder)

    objects = CdnConfigContextQuerySet.as_manager()

    clone_fields = [
       "name",
       "weight",
       "is_active",
       "schema",
       "regions",
       "cdnsites",
       "locations",
       "cdn_site_roles",
       "tags",
       "data",
    ]

    class Meta:
        ordering = ["weight", "name"]
        unique_together = [["name", "owner_content_type", "owner_object_id"]]

    def __str__(self):
        if self.owner:
            return f"[{self.owner}] {self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:cdnconfigcontext", kwargs={"pk": self.pk})

    def clean(self):
        super().clean()

        # Verify that JSON data is provided as an object
        if not isinstance(self.data, dict):
            raise ValidationError({"data": 'JSON data must be in object form. Example: {"foo": 123}'})

        # Validate data against schema
        self._validate_with_schema("data", "schema")

        # Check for a duplicated `name`. This is necessary because Django does not consider two NULL fields to be equal,
        # and thus if the `owner` is NULL, a duplicate `name` will not otherwise automatically raise an exception.
        if (
            CdnConfigContext.objects.exclude(pk=self.pk)
            .filter(name=self.name, owner_content_type=self.owner_content_type, owner_object_id=self.owner_object_id)
            .exists()
        ):
            raise ValidationError({"name": "A ConfigContext with this name already exists."})


class CdnConfigContextModel(models.Model, ConfigContextSchemaValidationMixin):
    """
    A model which includes local configuration context data. This local data will override any inherited data from
    ConfigContexts.
    """

    local_context_data = models.JSONField(
        encoder=DjangoJSONEncoder,
        blank=True,
        null=True,
    )
    local_context_schema = models.ForeignKey(
        to="extras.ConfigContextSchema",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional schema to validate the structure of the data",
    )
    # The local context data *may* be owned by another model, such as a GitRepository, or it may be un-owned
    local_context_data_owner_content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=FeatureQuery("config_context_owners"),
        default=None,
        null=True,
        blank=True,
    )
    local_context_data_owner_object_id = models.UUIDField(default=None, null=True, blank=True)
    local_context_data_owner = GenericForeignKey(
        ct_field="local_context_data_owner_content_type",
        fk_field="local_context_data_owner_object_id",
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=("local_context_data_owner_content_type", "local_context_data_owner_object_id")),
        ]

    def get_config_context(self):
        """
        Return the rendered configuration context for a device or VM.
        """

        if not hasattr(self, "config_context_data"):
            # Annotation not available, so fall back to manually querying for the config context
            config_context_data = CdnConfigContext.objects.get_for_object(self).values_list("data", flat=True)
        else:
            config_context_data = self.config_context_data or []
            # Annotation has keys "weight" and "name" (used for ordering) and "data" (the actual config context data)
            config_context_data = [
                c["data"] for c in sorted(config_context_data, key=lambda k: (k["weight"], k["name"]))
            ]

        # Compile all config data, overwriting lower-weight values with higher-weight values where a collision occurs
        data = OrderedDict()
        for context in config_context_data:
            data = deepmerge(data, context)

        # If the object has local config context data defined, merge it last
        if self.local_context_data:
            data = deepmerge(data, self.local_context_data)

        return data

    def clean(self):
        super().clean()

        # Verify that JSON data is provided as an object
        if self.local_context_data and not isinstance(self.local_context_data, dict):
            raise ValidationError({"local_context_data": 'JSON data must be in object form. Example: {"foo": 123}'})

        if self.local_context_schema and not self.local_context_data:
            raise ValidationError({"local_context_schema": "Local context data must exist for a schema to be applied."})

        # Validate data against schema
        self._validate_with_schema("local_context_data", "local_context_schema")


@extras_features(
    "custom_fields",
    "custom_validators",
    "graphql",
    "relationships",
)
class CdnConfigContextSchema(OrganizationalModel):
    """
    This model stores jsonschema documents where are used to optionally validate config context data payloads.
    """

    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)
    slug = AutoSlugField(populate_from="name", max_length=200, unique=None, db_index=True)
    data_schema = models.JSONField(
        help_text="A JSON Schema document which is used to validate a config context object."
    )
    # A ConfigContextSchema *may* be owned by another model, such as a GitRepository, or it may be un-owned
    owner_content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=FeatureQuery("config_context_owners"),
        default=None,
        null=True,
        blank=True,
    )
    owner_object_id = models.UUIDField(default=None, null=True, blank=True)
    owner = GenericForeignKey(
        ct_field="owner_content_type",
        fk_field="owner_object_id",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "owner_content_type", "owner_object_id"], name="cdn_unique_name_owner"),
        ]

    def __str__(self):
        if self.owner:
            return f"[{self.owner}] {self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:cdnconfigcontextschema", args=[self.slug])

    def clean(self):
        """
        Validate the schema
        """
        super().clean()

        try:
            Draft7Validator.check_schema(self.data_schema)
        except SchemaError as e:
            raise ValidationError({"data_schema": e.message})

        if (
            not isinstance(self.data_schema, dict)
            or "properties" not in self.data_schema
            or self.data_schema.get("type") != "object"
        ):
            raise ValidationError(
                {
                    "data_schema": "Nautobot only supports context data in the form of an object and thus the "
                    "JSON schema must be of type object and specify a set of properties."
                }
            )