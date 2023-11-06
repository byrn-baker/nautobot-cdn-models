import json
from collections import OrderedDict

from db_file_storage.model_utils import delete_file, delete_file_if_needed
from db_file_storage.storage import DatabaseFileStorage
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponse
from graphene_django.settings import graphene_settings
from graphql import get_default_backend
from graphql.error import GraphQLSyntaxError
from graphql.language.ast import OperationDefinition
from jsonschema.exceptions import SchemaError, ValidationError as JSONSchemaValidationError
from jsonschema.validators import Draft7Validator
from rest_framework.utils.encoders import JSONEncoder
from django.urls import reverse

from nautobot.core.models import BaseManager, BaseModel
from nautobot.core.models.fields import ForeignKeyWithAutoRelatedName
from nautobot.core.models.generics import OrganizationalModel
from nautobot.core.utils.data import deepmerge, render_jinja2
from nautobot.extras.choices import (
    ButtonClassChoices,
    WebhookHttpMethodChoices,
)
from nautobot.extras.constants import HTTP_CONTENT_TYPE_JSON
import nautobot.extras as extras
from nautobot.extras.models.models import ChangeLoggedModel, ConfigContextSchemaValidationMixin
from nautobot.extras.models.mixins import NotesMixin
from nautobot.extras.models.relationships import RelationshipModel
from nautobot.extras.querysets import NotesQuerySet
from nautobot.extras.utils import extras_features, FeatureQuery, image_upload

from ..querysets import RedirectMapContextQuerySet

@extras_features("graphql")
class RedirectMapContext(BaseModel, ChangeLoggedModel, ConfigContextSchemaValidationMixin, NotesMixin):
    """
    A RedirectMapContext represents a set of arbitrary data available to any CDN Site matching its assigned
    qualifiers (location, etc.). For example, the data stored in a RedirectMapContext assigned to location A will be available 
    to a Site in location A. Data is stored in JSON format.
    """

    name = models.CharField(max_length=100, unique=True)

    # A RedirectMapContext *may* be owned by another model, such as a GitRepository, or it may be un-owned
    owner_content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=FeatureQuery("redirectmap_context_owners"),
        default=None,
        null=True,
        blank=True,
        related_name="cdnsite_config_contexts",
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
        related_name="cdnsite_config_contexts",
    )
    locations = models.ManyToManyField(to="dcim.Location", related_name="+", blank=True)
    # TODO(timizuo): Find a way to limit role choices to cdnsite; as of now using
    #  limit_choices_to=Role.objects.get_for_model(Device), causes a partial import error
    cdn_site_roles = models.ManyToManyField(to="SiteRole", related_name="+", blank=True)
    cdnsites = models.ManyToManyField(to="CdnSite", related_name="+", blank=True)
    tags = models.ManyToManyField(to="extras.Tag", related_name="+", blank=True)

    data = models.JSONField(encoder=DjangoJSONEncoder)

    objects = BaseManager.from_queryset(RedirectMapContextQuerySet)()

    documentation_static_path = "docs/user-guide/core-data-model/extras/configcontext.html"
    
    clone_fields = [
       "name",
       "weight",
       "is_active",
       "schema",
       "cdnsites",
       "locations",
       "cdn_site_roles",
       "data",
    ]

    class Meta:
        ordering = ["weight", "name"]

    def __str__(self):
        if self.owner:
            return f"[{self.owner}] {self.name}"
        return self.name
    
    def get_absolute_url(self):
        return reverse("plugins:nautobot_cdn_models:redirectmapcontext", kwargs={"pk": self.pk})

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
            RedirectMapContext.objects.exclude(pk=self.pk)
            .filter(name=self.name, owner_content_type=self.owner_content_type, owner_object_id=self.owner_object_id)
            .exists()
        ):
            raise ValidationError({"name": "A RedirectMapContext with this name already exists."})


class RedirectMapContextModel(models.Model, ConfigContextSchemaValidationMixin):
    """
    A model which includes local configuration context data. This local data will override any inherited data from
    RedirectMapContexts.
    """

    local_redirectmap_context_data = models.JSONField(
        encoder=DjangoJSONEncoder,
        blank=True,
        null=True,
    )
    local_redirectmap_context_schema = ForeignKeyWithAutoRelatedName(
        to="extras.ConfigContextSchema",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional schema to validate the structure of the data",
    )
    # The local context data *may* be owned by another model, such as a GitRepository, or it may be un-owned
    local_redirectmap_context_data_owner_content_type = ForeignKeyWithAutoRelatedName(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=FeatureQuery("redirectmap_context_owners"),
        default=None,
        null=True,
        blank=True,
    )
    local_redirectmap_context_data_owner_object_id = models.UUIDField(default=None, null=True, blank=True)
    local_redirectmap_context_data_owner = GenericForeignKey(
        ct_field="local_redirectmap_context_data_owner_content_type",
        fk_field="local_redirectmap_context_data_owner_object_id",
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(
                fields=("local_redirectmap_context_data_owner_content_type", "local_redirectmap_context_data_owner_object_id")
            ),
        ]

    def get_redirectmap_context(self):
        """
        Return the rendered configuration context for a device or VM.
        """

        if not hasattr(self, "config_context_data"):
            # Annotation not available, so fall back to manually querying for the config context
            config_context_data = RedirectMapContext.objects.get_for_object(self).values_list("data", flat=True)
        else:
            config_context_data = self.config_context_data or []
            # Device and VirtualMachine's Location has its own RedirectMapContext and its parent Locations' RedirectMapContext, if any, should
            # also be applied. However, since moving from mptt to django-tree-queries https://github.com/nautobot/nautobot/issues/510,
            # we lost the ability to query the ancestors for a particular tree node for subquery https://github.com/matthiask/django-tree-queries/issues/54.
            # So instead of constructing the location related query in RedirectMapContextModelQueryset._get_redirectmap_context_filters(), which is complicated across databases
            # We append the missing parent location query here as a patch.
            location_redirectmap_context_queryset = RedirectMapContext.objects.none()
            if self._meta.model_name == "device":
                location_redirectmap_context_queryset = RedirectMapContext.objects.filter(
                    locations__in=self.location.ancestors(include_self=True)
                ).distinct()
            else:
                if self.cluster and self.cluster.location:
                    location_redirectmap_context_queryset = RedirectMapContext.objects.filter(
                        locations__in=self.cluster.location.ancestors(include_self=True)
                    ).distinct()

            # Annotation has keys "weight" and "name" (used for ordering) and "data" (the actual config context data)
            for cc in location_redirectmap_context_queryset:
                config_context_data.append({"data": cc.data, "name": cc.name, "weight": cc.weight})
            config_context_data = [
                c["data"] for c in sorted(config_context_data, key=lambda k: (k["weight"], k["name"]))
            ]

        # Compile all config data, overwriting lower-weight values with higher-weight values where a collision occurs
        data = OrderedDict()
        for context in config_context_data:
            data = deepmerge(data, context)

        # If the object has local config context data defined, merge it last
        if self.local_redirectmap_context_data:
            data = deepmerge(data, self.local_redirectmap_context_data)

        return data

    def clean(self):
        super().clean()

        # Verify that JSON data is provided as an object
        if self.local_redirectmap_context_data and not isinstance(self.local_redirectmap_context_data, dict):
            raise ValidationError(
                {"local_redirectmap_context_data": 'JSON data must be in object form. Example: {"foo": 123}'}
            )

        if self.local_redirectmap_context_schema and not self.local_redirectmap_context_data:
            raise ValidationError(
                {"local_redirectmap_context_schema": "Local config context data must exist for a schema to be applied."}
            )

        # Validate data against schema
        self._validate_with_schema("local_redirectmap_context_data", "local_redirectmap_context_schema")