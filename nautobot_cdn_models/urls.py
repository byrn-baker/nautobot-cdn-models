from django.urls import path

from nautobot.extras.views import ObjectChangeLogView, ObjectNotesView
from . import views
from .models import CdnSite, SiteRole

app_name = "nautobot-cdn-models"
urlpatterns = [
    # CDn Site Roles
    path("cdn-site-roles", views.SiteRoleListView.as_view(), name="siterole_list"),
    path(
        "cdn-site-rolesadd/",
        views.SiteRoleEditView.as_view(),
        name="siterole_add",
    ),
    path(
        "cdn-site-rolesimport/",
        views.SiteRoleBulkImportView.as_view(),
        name="siterole_import",
    ),
    path(
        "cdn-site-rolesdelete/",
        views.SiteRoleBulkDeleteView.as_view(),
        name="siterole_bulk_delete",
    ),
    path(
        "cdn-site-roles<uuid:pk>/",
        views.SiteRoleView.as_view(),
        name="siterole",
    ),
    path(
        "cdn-site-roles<uuid:pk>/edit/",
        views.SiteRoleEditView.as_view(),
        name="siterole_edit",
    ),
    path(
        "cdn-site-roles<uuid:pk>/delete/",
        views.SiteRoleDeleteView.as_view(),
        name="siterole_delete",
    ),
    path(
        "cdn-site-roles<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="siterole_changelog",
        kwargs={"model": SiteRole},
    ),
    path(
        "cdn-site-roles<uuid:pk>/notes/",
        ObjectNotesView.as_view(),
        name="siterole_notes",
        kwargs={"model": SiteRole},
    ),
    # CDN Sites
    path("cdn-sites/", views.CdnSiteListView.as_view(), name="cdnsitelist"),
    path("cdn-sites/add/", views.CdnSiteEditView.as_view(), name="cdnsiteadd"),
    path("cdn-sites/import/", views.CdnSiteBulkImportView.as_view(), name="cdnsiteimport"),
    path("cdn-sites/edit/", views.CdnSiteBulkEditView.as_view(), name="cdnsitebulk_edit"),
    path(
        "cdn-sites/delete/",
        views.CdnSiteBulkDeleteView.as_view(),
        name="cdnsitebulk_delete",
    ),
    path("cdn-sites/<uuid:pk>/", views.CdnSiteView.as_view(), name="CdnSite"),
    path("cdn-sites/<uuid:pk>/edit/", views.CdnSiteEditView.as_view(), name="cdnsiteedit"),
    path(
        "cdn-sites/<uuid:pk>/delete/",
        views.CdnSiteDeleteView.as_view(),
        name="cdnsitedelete",
    ),
    path(
        "cdn-sites/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="cdnsitechangelog",
        kwargs={"model": CdnSite},
    ),
    path(
        "cdn-sites/<uuid:pk>/notes/",
        ObjectNotesView.as_view(),
        name="cdnsitenotes",
        kwargs={"model": CdnSite},
    ),
]