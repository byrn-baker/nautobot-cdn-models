from django.db.models import OuterRef, Subquery, Q, F
from django.db.models.functions import JSONObject
from deepmerge import always_merger

from nautobot.extras.models.tags import TaggedItem
from nautobot.utilities.query_functions import EmptyGroupByJSONBAgg
from nautobot.utilities.querysets import RestrictedQuerySet



class CdnConfigContextQuerySet(RestrictedQuerySet):
    def get_for_object(self, obj):
        """
        Return all applicable ConfigContexts for a given object. Only active ConfigContexts will be included.
        """
        # `site_role` for CdnSite
        cdn_site_role = getattr(obj, "cdn_site_role", None) or obj.cdn_site_role

        # Match against the directly assigned region as well as any parent regions.
        region = getattr(obj, "region", None)
        if region:
            regions = region.get_ancestors(include_self=True)
        else:
            regions = []

        # Match against the directly assigned location as well as any parent locations
        location = getattr(obj, "location", None)
        if location:
            locations = location.ancestors(include_self=True)
        else:
            locations = []

        query = [
            Q(regions__in=regions) | Q(regions=None),
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


class CdnConfigContextModelQuerySet(RestrictedQuerySet):
    """
    QuerySet manager used by models which support CdnConfigContext (CdnSite).

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
        from .models.contexts import CdnConfigContext
        
        return self.annotate(
            config_context_data=Subquery(
                CdnConfigContext.objects.filter(self._get_config_context_filters())
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
        # Construct the set of Q objects for the specific object types
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

        if self.model._meta.model_name == "cdnsite":
            base_query.add((Q(cdn_site_roles=OuterRef("cdn_site_role")) | Q(cdn_site_roles=None)), Q.AND)
            region_field = "region"

        base_query.add(
            (
                Q(
                    regions__tree_id=OuterRef(f"{region_field}__tree_id"),
                    regions__level__lte=OuterRef(f"{region_field}__level"),
                    regions__lft__lte=OuterRef(f"{region_field}__lft"),
                    regions__rght__gte=OuterRef(f"{region_field}__rght"),
                )
                | Q(regions=None)
            ),
            Q.AND,
        )

        return base_query

class CdnOriginContextQuerySet(RestrictedQuerySet):
    def get_for_object(self, obj):
        """
        Return all applicable OriginContexts for a given object. Only active OriginContexts will be included.
        """
        # `cdn_origin` for origin
        cdn_origin = getattr(obj, "cdn_origin", None) or obj.cdn_origin

        query = [
            Q(cdn_origin=obj.id) | Q(cdn_origin=None),
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