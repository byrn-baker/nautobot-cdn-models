from nautobot.core.api.routers import OrderedDefaultRouter

from . import views

router = OrderedDefaultRouter()
router.register("hypercachememoryprofile", views.HyperCacheMemoryProfileViewSet)
router.register("siterole", views.SiteRoleViewSet)
router.register("cdnsite", views.CdnSiteViewSet)
router.register("cdn-redirect-map-contexts", views.RedirectMapContextViewSet)

urlpatterns = router.urls