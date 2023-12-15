from django.urls import path

from nautobot.core.views.routers import NautobotUIViewSetRouter
from nautobot.extras.views import ObjectNotesView
from . import views
from .models import (
    CdnConfigContext,
    SiteRole
)

app_name = "cdn"

router = NautobotUIViewSetRouter()
router.register("hypercachememoryprofiles", views.HyperCacheMemoryProfileUIViewSet)
router.register("serviceproviders", views.ServiceProviderUIViewSet)
router.register("contentproviders", views.ContentProviderUIViewSet)
router.register("origins", views.OriginUIViewSet)
router.register("cdnprefix", views.CdnPrefixUIViewSet)
router.register("cdnprefixdefaultbehavior", views.CdnPrefixDefaultBehaviorUIViewSet)
router.register("cdnprefixbehavior", views.CdnPrefixBehaviorUIViewSet)

urlpatterns = [
    path("siteroles/", views.SiteRoleListView.as_view(), name="siterole_list"),
    path("siteroles/", views.SiteRoleListView.as_view(), name="siterole_list"),
    path(
        "siteroles/add/",
        views.SiteRoleEditView.as_view(),
        name="siterole_add",
    ),
    path(
        "siteroles/import/",
        views.SiteRoleBulkImportView.as_view(),
        name="siterole_import",
    ),
    path(
        "siteroles/delete/",
        views.SiteRoleBulkDeleteView.as_view(),
        name="siterole_bulk_delete",
    ),
    path(
        "siteroles/<slug:slug>/",
        views.SiteRoleView.as_view(),
        name="siterole",
    ),
    path(
        "siteroles/<slug:slug>/edit/",
        views.SiteRoleEditView.as_view(),
        name="siterole_edit",
    ),
    path(
        "siteroles/<slug:slug>/delete/",
        views.SiteRoleDeleteView.as_view(),
        name="siterole_delete",
    ),
    path(
        "siteroles/<slug:slug>/changelog/",
        views.ObjectChangeLogView.as_view(),
        name="siterole_changelog",
        kwargs={"model": SiteRole},
    ),
    path(
        "siteroles/<slug:slug>/notes/",
        ObjectNotesView.as_view(),
        name="siterole_notes",
        kwargs={"model": SiteRole},
    ),
    path("cdnsites/", views.CdnSiteListView.as_view(), name="cdnsite_list"),
    path("cdnsites/add/", views.CdnSiteEditView.as_view(), name="cdnsite_add"),
    path("cdnsites/import/", views.CdnSiteBulkImportView.as_view(), name="cdnsite_import"),
    path("cdnsites/edit/", views.CdnSiteBulkEditView.as_view(), name="cdnsite_bulk_edit"),
    path("cdnsites/delete/", views.CdnSiteBulkDeleteView.as_view(), name="cdnsite_bulk_delete"),
    path("cdnsites/<uuid:pk>/", views.CdnSiteView.as_view(), name="cdnsite"),
    path("cdnsites/<uuid:pk>/edit/", views.CdnSiteEditView.as_view(), name="cdnsite_edit"),
    path("cdnsites/<uuid:pk>/delete/", views.CdnSiteDeleteView.as_view(), name="cdnsite_delete"),
    path(
        "cdnsites/<uuid:pk>/cdn-config-context/",
        views.CdnSiteConfigContextView.as_view(),
        name="cdnsite_cdnconfigcontext",
    ),
    path(
        "devices/<uuid:pk>/device_detail_tab/",
        views.DeviceDetailPluginView.as_view(),
        name="device_detail_tab",
    ),
    # Config contexts
    path(
        "cdnconfig-contexts/",
        views.CdnConfigContextListView.as_view(),
        name="cdnconfigcontext_list",
    ),
    path(
        "cdnconfig-contexts/add/",
        views.CdnConfigContextEditView.as_view(),
        name="cdnconfigcontext_add",
    ),
    path(
        "cdnconfig-contexts/edit/",
        views.CdnConfigContextBulkEditView.as_view(),
        name="cdnconfigcontext_bulk_edit",
    ),
    path(
        "cdnconfig-contexts/delete/",
        views.CdnConfigContextBulkDeleteView.as_view(),
        name="cdnconfigcontext_bulk_delete",
    ),
    path(
        "cdnconfig-contexts/<uuid:pk>/",
        views.CdnConfigContextView.as_view(),
        name="cdnconfigcontext",
    ),
    path(
        "cdnconfig-contexts/<uuid:pk>/edit/",
        views.CdnConfigContextEditView.as_view(),
        name="cdnconfigcontext_edit",
    ),
    path(
        "cdnconfig-contexts/<uuid:pk>/delete/",
        views.CdnConfigContextDeleteView.as_view(),
        name="cdnconfigcontext_delete",
    ),
    path(
        "cdnconfig-contexts/<uuid:pk>/changelog/",
        views.ObjectChangeLogView.as_view(),
        name="cdnconfigcontext_changelog",
        kwargs={"model": CdnConfigContext},
    ),
    path(
        "cdnconfig-contexts/<uuid:pk>/notes/",
        ObjectNotesView.as_view(),
        name="cdnconfigcontext_notes",
        kwargs={"model": CdnConfigContext},
    ),
]
urlpatterns += router.urls
