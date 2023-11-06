from django.db.models import OuterRef, Subquery, Q, F
from django.db.models.functions import JSONObject
from deepmerge import always_merger

from nautobot.extras.models.tags import TaggedItem
from nautobot.utilities.query_functions import EmptyGroupByJSONBAgg
from nautobot.utilities.querysets import RestrictedQuerySet

from django.core.cache import cache
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, OuterRef, Subquery, Q, F
from django.db.models.functions import JSONObject
from django_celery_beat.managers import ExtendedQuerySet

from nautobot.core.models.querysets import RestrictedQuerySet
from nautobot.core.models.query_functions import EmptyGroupByJSONBAgg
from nautobot.core.utils.config import get_settings_or_config
from nautobot.extras.models.tags import TaggedItem



class RedirectMapContextQuerySet(RestrictedQuerySet):
    def get_for_object(self, obj):
        """
        Return all applicable ConfigContexts for a given object. Only active ConfigContexts will be included.
        """
        # `site_role` for CdnSite
        cdn_site_role = getattr(obj, "cdn_site_role", None) or obj.cdn_site_role

        # Match against the directly assigned location as well as any parent locations
        location = getattr(obj, "location", None)
        if location:
            locations = location.ancestors(include_self=True)
        else:
            locations = []

        query = [
            Q(cdnsites=obj.id) | Q(cdnsites=None),
            Q(locations__in=locations) | Q(locations=None),
            Q(cdn_site_roles=cdn_site_role) | Q(cdn_site_roles=None),
            Q(tags__slug__in=obj.tags.slugs()) | Q(tags=None),
        ]

        queryset = (
            self.filter(
                *query,
                is_active=True,
            )
            .order_by("weight", "name")
            .distinct()
        )

        return queryset

class RedirectMapContextModelQuerySet(RestrictedQuerySet):
    """
    QuerySet manager used by models which support RedirectMapContext (CdnSite).

    Includes a method which appends an annotation of aggregated config context JSON data objects. This is
    implemented as a subquery which performs all the joins necessary to filter relevant config context objects.
    This offers a substantial performance gain over ConfigContextQuerySet.get_for_object() when dealing with
    multiple objects.

    This allows the annotation to be entirely optional.
    """

    def annotate_config_context_data(self):
        """
        Attach the subquery annotation to the base queryset.

        Order By clause in Subquery is not guaranteed to be respected within the aggregated JSON array, which is why
        we include "weight" and "name" into the result so that we can sort it within Python to ensure correctness.
        """
        from .models.redirectmap import RedirectMapContext
        
        return self.annotate(
            config_context_data=Subquery(
                RedirectMapContext.objects.filter(self._get_config_context_filters())
                .order_by("weight", "name")
                .annotate(
                    _data=EmptyGroupByJSONBAgg(
                        JSONObject(
                            data=F("data"),
                            name=F("name"),
                            weight=F("weight"),
                        )
                    )
                )
                .values("_data")
            )
        ).distinct()

    def _get_config_context_filters(self):
        """
        This method is constructing the set of Q objects for the specific object types.
        Note that locations filters are not included in the method because the filter needs the
        ability to query the ancestors for a particular tree node for subquery and we lost it since
        moving from mptt to django-tree-queries https://github.com/matthiask/django-tree-queries/issues/54.
        """
        tag_query_filters = {
            "object_id": OuterRef(OuterRef("pk")),
            "content_type__app_label": self.model._meta.app_label,
            "content_type__model": self.model._meta.model_name,
        }
        base_query = Q(
            Q(tags__pk__in=Subquery(TaggedItem.objects.filter(**tag_query_filters).values_list("tag_id", flat=True)))
            | Q(tags=None),
            is_active=True,
        )
        base_query.add((Q(cdn_site_roles=OuterRef("cdn_site_role")) | Q(cdn_site_roles=None)), Q.AND)
        if self.model._meta.model_name == "cdnsite":
            base_query.add((Q(device_types=OuterRef("device_type")) | Q(device_types=None)), Q.AND)
            # This is necessary to prevent location related config context to be applied now.
            # The location hierarchy cannot be processed by the database and must be added by `ConfigContextModel.get_config_context`
            base_query.add((Q(locations=None)), Q.AND)

        return base_query