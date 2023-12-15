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

class CdnConfigContextType(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = models.CdnConfigContext
        filterset_set = filters.CdnConfigContextFilterSet
        exclude = ["_name"]

class ContentProviderType(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = models.ContentProvider
        filterset_set = filters.ContentProviderFilterSet
        exclude = ["_name"]

class ServiceProviderType(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = models.ServiceProvider
        filterset_set = filters.ServiceProviderFilterSet
        exclude = ["_name"]

class OriginType(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = models.Origin
        filterset_set = filters.OriginFilterSet
        exclude = ["_name"]
        
class CdnPrefixType(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = models.CdnPrefix
        filterset_set = filters.CdnPrefixFilterSet
        exclude = ["_name"]
        
class CdnPrefixDefaultBehaviorType(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = models.CdnPrefixDefaultBehavior
        filterset_set = filters.CdnPrefixDefaultBehaviorFilterSet
        exclude = ["_name"]
        
class CdnPrefixBehaviorType(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = models.CdnPrefixBehavior
        filterset_set = filters.CdnPrefixBehaviorFilterSet
        exclude = ["_name"]

graphql_types = [HyperCacheMemoryProfileType, SiteRoleType, CdnSiteType, CdnConfigContextType, ServiceProviderType, ContentProviderType, OriginType, CdnPrefixType, CdnPrefixDefaultBehaviorType, CdnPrefixBehaviorType]