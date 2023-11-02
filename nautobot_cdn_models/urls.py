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
# router.register("siteroles", views.SiteRoleUIViewSet)

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
    path("cdnsites/<uuid:pk>/", views.CdnSiteView.as_view(), name="cdnsite"),
    path("cdnsites/<uuid:pk>/edit/", views.CdnSiteEditView.as_view(), name="cdnsite_edit"),
    path("cdnsites/<uuid:pk>/delete/", views.CdnSiteDeleteView.as_view(), name="cdnsite_delete"),
    path(
        "cdnsites/<uuid:pk>/cdn-config-context/",
        views.CdnSiteConfigContextView.as_view(),
        name="cdnsite_cdnconfigcontext",
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
    # Config context schema
    # path(
    #     "cdnconfig-context-schemas/",
    #     views.CdnConfigContextSchemaListView.as_view(),
    #     name="cdnconfigcontextschema_list",
    # ),
    # path(
    #     "cdnconfig-context-schemas/add/",
    #     views.CdnConfigContextSchemaEditView.as_view(),
    #     name="cdnconfigcontextschema_add",
    # ),
    # path(
    #     "cdnconfig-context-schemas/edit/",
    #     views.CdnConfigContextSchemaBulkEditView.as_view(),
    #     name="cdnconfigcontextschema_bulk_edit",
    # ),
    # path(
    #     "cdnconfig-context-schemas/delete/",
    #     views.CdnConfigContextSchemaBulkDeleteView.as_view(),
    #     name="cdnconfigcontextschema_bulk_delete",
    # ),
    # path(
    #     "cdnconfig-context-schemas/<slug:slug>/",
    #     views.CdnConfigContextSchemaView.as_view(),
    #     name="cdnconfigcontextschema",
    # ),
    # path(
    #     "cdnconfig-context-schemas/<slug:slug>/validation/",
    #     views.CdnConfigContextSchemaObjectValidationView.as_view(),
    #     name="cdnconfigcontextschema_object_validation",
    # ),
    # path(
    #     "cdnconfig-context-schemas/<slug:slug>/edit/",
    #     views.CdnConfigContextSchemaEditView.as_view(),
    #     name="cdnconfigcontextschema_edit",
    # ),
    # path(
    #     "cdnconfig-context-schemas/<slug:slug>/delete/",
    #     views.CdnConfigContextSchemaDeleteView.as_view(),
    #     name="cdnconfigcontextschema_delete",
    # ),
    # path(
    #     "cdnconfig-context-schemas/<slug:slug>/changelog/",
    #     views.ObjectChangeLogView.as_view(),
    #     name="cdnconfigcontextschema_changelog",
    #     kwargs={"model": CdnConfigContextSchema},
    # ),
    # path(
    #     "cdnconfig-context-schemas/<slug:slug>/notes/",
    #     ObjectNotesView.as_view(),
    #     name="cdnconfigcontextschema_notes",
    #     kwargs={"model": CdnConfigContextSchema},
    # ),
]
urlpatterns += router.urls