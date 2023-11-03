import django_filters

from nautobot.core.filters import NaturalKeyOrPKMultipleChoiceFilter, TreeNodeMultipleChoiceFilter
from ..models import CdnSite, SiteRole


class CdnSiteModelFilterSetMixin(django_filters.FilterSet):
    """
    An inheritable FilterSet for models which support Cdnsite assignment.
    """

    site_role = TreeNodeMultipleChoiceFilter(
        queryset=SiteRole.objects.all(),
        field_name="cdnsite__site_role",
        to_field_name="name",
        label="Site Role (name or ID)",
    )
    cdnsite_id = django_filters.ModelMultipleChoiceFilter(
        queryset=CdnSite.objects.all(),
        label='Cdnsite (ID) (deprecated, use "Cdnsite" filter instead)',
    )
    cdnsite = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=cdnsite_id.objects.all(),
        to_field_name="name",
        label="Cdnsite (name or ID)",
    )