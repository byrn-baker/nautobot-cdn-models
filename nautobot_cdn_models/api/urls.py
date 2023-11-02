from nautobot.core.api import OrderedDefaultRouter

from . import views

router = OrderedDefaultRouter()
router.register("hypercachememoryprofile", views.HyperCacheMemoryProfileViewSet)
router.register("siterole", views.SiteRoleViewSet)
router.register("cdnsite", views.CdnSiteViewSet)
# Config contexts
router.register("cdnconfig-contexts", views.CdnConfigContextViewSet)
# Config context schemas
# router.register("cdnconfig-context-schemas", views.CdnConfigContextSchemaViewSet)

urlpatterns = router.urls