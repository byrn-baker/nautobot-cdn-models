from django.urls import path

from nautobot.extras.views import ObjectChangeLogView, ObjectNotesView
from . import views
from .models import CdnSite, SiteRole, HyperCacheMemoryProfile, RedirectMapContext

app_name = "nautobot_cdn_models"

urlpatterns = [
    # HyperCacheMemoryProfiles
    path("hypercache-memory-profiles/", views.HyperCacheMemoryProfileListView.as_view(), name="hypercachememoryprofile_list"),
    path(
        "hypercache-memory-profiles/add/",
        views.HyperCacheMemoryProfileEditView.as_view(),
        name="hypercachememoryprofile_add",
    ),
    path(
        "hypercache-memory-profiles/import/",
        views.HyperCacheMemoryProfileBulkImportView.as_view(),
        name="hypercachememoryprofile_import",
    ),
    path(
        "hypercache-memory-profiles/delete/",
        views.HyperCacheMemoryProfileBulkDeleteView.as_view(),
        name="hypercachememoryprofile_bulk_delete",
    ),
    path(
        "hypercache-memory-profiles/<uuid:pk>/",
        views.HyperCacheMemoryProfileView.as_view(),
        name="hypercachememoryprofile",
    ),
    path(
        "hypercache-memory-profiles/<uuid:pk>/edit/",
        views.HyperCacheMemoryProfileEditView.as_view(),
        name="hypercachememoryprofile_edit",
    ),
    path(
        "hypercache-memory-profiles/<uuid:pk>/delete/",
        views.HyperCacheMemoryProfileDeleteView.as_view(),
        name="hypercachememoryprofile_delete",
    ),
    path(
        "hypercache-memory-profiles/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="hypercachememoryprofile_changelog",
        kwargs={"model": HyperCacheMemoryProfile},
    ),
    path(
        "hypercache-memory-profiles/<uuid:pk>/notes/",
        ObjectNotesView.as_view(),
        name="hypercachememoryprofile_notes",
        kwargs={"model": HyperCacheMemoryProfile},
    ),
    # CDN Site Roles
    path("cdn-site-roles/", views.SiteRoleListView.as_view(), name="siterole_list"),
    path(
        "cdn-site-roles/add/",
        views.SiteRoleEditView.as_view(),
        name="siterole_add",
    ),
    path(
        "cdn-site-roles/import/",
        views.SiteRoleBulkImportView.as_view(),
        name="siterole_import",
    ),
    path(
        "cdn-site-roles/delete/",
        views.SiteRoleBulkDeleteView.as_view(),
        name="siterole_bulk_delete",
    ),
    path(
        "cdn-site-roles/<uuid:pk>/",
        views.SiteRoleView.as_view(),
        name="siterole",
    ),
    path(
        "cdn-site-roles/<uuid:pk>/edit/",
        views.SiteRoleEditView.as_view(),
        name="siterole_edit",
    ),
    path(
        "cdn-site-roles/<uuid:pk>/delete/",
        views.SiteRoleDeleteView.as_view(),
        name="siterole_delete",
    ),
    path(
        "cdn-site-roles/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="siterole_changelog",
        kwargs={"model": SiteRole},
    ),
    # path(
    #     "cdn-site-roles/<uuid:pk>/notes/",
    #     ObjectNotesView.as_view(),
    #     name="siterole_notes",
    #     kwargs={"model": SiteRole},
    # ),
    # CDN Sites
    path("cdn-sites/", views.CdnSiteListView.as_view(), name="cdnsite_list"),
    path("cdn-sites/add/", views.CdnSiteEditView.as_view(), name="cdnsite_add"),
    path("cdn-sites/import/", views.CdnSiteBulkImportView.as_view(), name="cdnsite_import"),
    path("cdn-sites/edit/", views.CdnSiteBulkEditView.as_view(), name="cdnsite_bulkedit"),
    path(
        "cdn-sites/delete/",
        views.CdnSiteBulkDeleteView.as_view(),
        name="cdnsitebulk_delete",
    ),
    path("cdn-sites/<uuid:pk>/", views.CdnSiteView.as_view(), name="cdnsite"),
    path("cdn-sites/<uuid:pk>/edit/", views.CdnSiteEditView.as_view(), name="cdnsite_edit"),
    path(
        "cdn-sites/<uuid:pk>/delete/",
        views.CdnSiteDeleteView.as_view(),
        name="cdnsite_delete",
    ),
    path(
        "cdn-sites/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="cdnsite_changelog",
        kwargs={"model": CdnSite},
    ),
    # path(
    #     "cdn-sites/<uuid:pk>/notes/",
    #     ObjectNotesView.as_view(),
    #     name="cdnsite_notes",
    #     kwargs={"model": CdnSite},
    # ),
    # Config contexts
    path(
        "cdn-redirect-map-contexts/",
        views.RedirectMapContextListView.as_view(),
        name="redirectmapcontext_list",
    ),
    path(
        "cdn-redirect-map-contexts/add/",
        views.RedirectMapContextEditView.as_view(),
        name="redirectmapcontext_add",
    ),
    path(
        "cdn-redirect-map-contexts/edit/",
        views.RedirectMapContextBulkEditView.as_view(),
        name="redirectmapcontext_bulk_edit",
    ),
    path(
        "cdn-redirect-map-contexts/delete/",
        views.RedirectMapContextBulkDeleteView.as_view(),
        name="redirectmapcontext_bulk_delete",
    ),
    path(
        "cdn-redirect-map-contexts/<uuid:pk>/",
        views.RedirectMapContextView.as_view(),
        name="redirectmapcontext",
    ),
    path(
        "cdn-redirect-map-contexts/<uuid:pk>/edit/",
        views.RedirectMapContextEditView.as_view(),
        name="redirectmapcontext_edit",
    ),
    path(
        "cdn-redirect-map-contexts/<uuid:pk>/delete/",
        views.RedirectMapContextDeleteView.as_view(),
        name="redirectmapcontext_delete",
    ),
    path(
        "cdn-redirect-map-contexts/<uuid:pk>/changelog/",
        views.ObjectChangeLogView.as_view(),
        name="redirectmapcontext_changelog",
        kwargs={"model": RedirectMapContext},
    ),
    # path(
    #     "cdn-redirect-map-contexts/<uuid:pk>/notes/",
    #     ObjectNotesView.as_view(),
    #     name="redirectmapcontext_notes",
    #     kwargs={"model": RedirectMapContext},
    # ),
]