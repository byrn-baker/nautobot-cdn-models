from nautobot.core.api import OrderedDefaultRouter

from . import views

router = OrderedDefaultRouter()
router.register("hypercachememoryprofile", views.HyperCacheMemoryProfileViewSet)
router.register("siterole", views.SiteRoleViewSet)
router.register("cdnsite", views.CdnSiteViewSet)
# Config contexts
router.register("cdnconfig-contexts", views.CdnConfigContextViewSet)
# Content Delivery
router.register("serviceprovider", views.ServiceProviderViewSet)
router.register("contentprovider", views.ContentProviderViewSet)
router.register("originprovider", views.OriginViewSet)
urlpatterns = router.urls