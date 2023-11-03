from nautobot.core.api.routers import OrderedDefaultRouter

from . import views

router = OrderedDefaultRouter()
router.register("hypercachememoryprofile", views.HyperCacheMemoryProfileViewSet)
router.register("siterole", views.SiteRoleViewSet)
router.register("cdnsite", views.CdnSiteViewSet)
# router.register("cdnconfig-contexts", views.CdnConfigContextViewSet)

urlpatterns = router.urls