import graphene_django_optimizer as gql_optimizer

from .. import models, filters

class HyperCacheMemoryProfileType(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = models.HyperCacheMemoryProfile
        filterset_set = filters.HyperCacheMemoryProfileFilterSet

class SiteRoleType(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = models.SiteRole
        filterset_set = filters.SiteRoleFilterSet

class CdnSiteType(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = models.CdnSite
        filterset_set = filters.CdnSiteFilterSet
        exclude = ["_name"]



graphql_types = [HyperCacheMemoryProfileType, SiteRoleType, CdnSiteType]