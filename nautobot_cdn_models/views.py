from django_tables2 import RequestConfig
from deepmerge import Merger
from jsonschema.validators import Draft7Validator
from django.urls import reverse

from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View

from nautobot.extras.utils import get_worker_count
from nautobot.core.views import generic, mixins as view_mixins
from nautobot.core.models.querysets import count_related
from nautobot.core.views.paginator import EnhancedPaginator, get_paginate_count
from nautobot.core.tables import ButtonsColumn
from nautobot.dcim.models import Device
from nautobot.extras.views import ObjectChangeLogView

from nautobot.extras.models import RelationshipAssociation, JobResult
from nautobot.extras.choices import JobResultStatusChoices
from nautobot.extras.tables import RelationshipAssociationTable
from nautobot.extras.datasources import (
    enqueue_git_repository_diff_origin_and_local,
    enqueue_pull_git_repository_and_refresh_data,
    get_datasource_contents,
)

from . import filters, tables, forms
from .models import CdnSite, SiteRole, HyperCacheMemoryProfile, RedirectMapContext, RedirectMapContextSchema, CdnGitRepository


## HyperCache Memory Profiles
class HyperCacheMemoryProfileListView(generic.ObjectListView):
    queryset = HyperCacheMemoryProfile.objects.all()
    filterset = filters.HyperCacheMemoryProfileFilterSet
    table = tables.HyperCacheMemoryProfileTable


class HyperCacheMemoryProfileView(generic.ObjectView):
    queryset = HyperCacheMemoryProfile.objects.all()


class HyperCacheMemoryProfileEditView(generic.ObjectEditView):
    queryset = HyperCacheMemoryProfile.objects.all()
    model_form = forms.HyperCacheMemoryProfileForm


class HyperCacheMemoryProfileDeleteView(generic.ObjectDeleteView):
    queryset = HyperCacheMemoryProfile.objects.all()


class HyperCacheMemoryProfileBulkImportView(generic.BulkImportView):
    queryset = HyperCacheMemoryProfile.objects.all()
    table = tables.HyperCacheMemoryProfileTable


class HyperCacheMemoryProfileBulkDeleteView(generic.BulkDeleteView):
    queryset = HyperCacheMemoryProfile.objects.all()
    table = tables.HyperCacheMemoryProfileTable
    filterset = filters.HyperCacheMemoryProfileFilterSet

## CDN Site Roles ##
class SiteRoleListView(generic.ObjectListView):
    queryset = SiteRole.objects.annotate(cdnsite_count=count_related(CdnSite, "cdn_site_role"))
    filterset = filters.SiteRoleFilterSet
    table = tables.SiteRoleTable


class SiteRoleView(generic.ObjectView):
    queryset = SiteRole.objects.all()

    def get_extra_context(self, request, instance):
        # CdnSite
        cdnsites = CdnSite.objects.restrict(request.user, "view").filter(
            cdn_site_role__in=instance.descendants(include_self=True)
        )

        cdnsite_table = tables.CdnSiteTable(cdnsites)
        cdnsite_table.columns.hide("cdn_site_role")

        paginate = {
            "paginator_class": EnhancedPaginator,
            "per_page": get_paginate_count(request),
        }
        RequestConfig(request, paginate).configure(cdnsite_table)

        return {
            "cdnsite_table": cdnsite_table,
        }


class SiteRoleEditView(generic.ObjectEditView):
    queryset = SiteRole.objects.all()
    model_form = forms.SiteRoleForm


class SiteRoleDeleteView(generic.ObjectDeleteView):
    queryset = SiteRole.objects.all()


class SiteRoleBulkImportView(generic.BulkImportView):
    queryset = SiteRole.objects.all()
    table = tables.SiteRoleTable


class SiteRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = SiteRole.objects.annotate(cdnsite_count=count_related(CdnSite, "cdn_site_role"))
    table = tables.SiteRoleTable
    filterset = filters.SiteRoleFilterSet

## CDN SITES ##
class CdnSiteListView(generic.ObjectListView):
    queryset = CdnSite.objects.select_related("cdn_site_role")
    filterset = filters.CdnSiteFilterSet
    filterset_form = forms.CdnSiteFilterForm
    table = tables.CdnSiteTable


class CdnSiteView(generic.ObjectView):
    queryset = CdnSite.objects.select_related("cdn_site_role")

    # def get_extra_context(self, request, instance):
    #     stats = {
    #         # TODO: Should we include child locations of the filtered locations in the location_count below?
    #         "location_count": Location.objects.restrict(request.user, "view").filter(cdnsites=instance).count(),
    #         "rack_count": Rack.objects.restrict(request.user, "view").filter(cdnsites=instance).count(),
    #         "rackreservation_count": RackReservation.objects.restrict(request.user, "view")
    #         .filter(cdnsites=instance)
    #         .count(),
    #         "device_count": Device.objects.restrict(request.user, "view").filter(cdnsites=instance).count(),
    #         "prefix_count": Prefix.objects.restrict(request.user, "view").filter(cdnsites=instance).count(),
    #         "ipaddress_count": IPAddress.objects.restrict(request.user, "view").filter(cdnsites=instance).count(),
    #         "virtualmachine_count": VirtualMachine.objects.restrict(request.user, "view")
    #         .filter(cdnsites=instance)
    #         .count(),
    #     }

    #     return {
    #         "stats": stats,
    #     }
    def get_extra_context(self, request, instance):
        stats = {
            "device_count": RelationshipAssociation.objects.all().filter(destination_id=instance.id).count()
        }
        return{
            "stats": stats
        }
    
    def get_extra_context(self, request, instance):
        relations = RelationshipAssociation.objects.all().filter(destination_id=instance.id)

        relation_table = RelationshipAssociationTable(relations)
        relation_table.columns.hide("destination")

        paginate = {
            "paginator_class": EnhancedPaginator,
            "per_page": get_paginate_count(request),
        }
        RequestConfig(request, paginate).configure(relation_table)

        return {
            "relation_table": relation_table
        }


class CdnSiteEditView(generic.ObjectEditView):
    queryset = CdnSite.objects.all()
    model_form = forms.CdnSiteForm
    template_name = "nautobot_cdn_models/cdnsite_edit.html"


class CdnSiteDeleteView(generic.ObjectDeleteView):
    queryset = CdnSite.objects.all()


class CdnSiteBulkImportView(generic.BulkImportView):
    queryset = CdnSite.objects.all()
    table = tables.CdnSiteTable


class CdnSiteBulkEditView(generic.BulkEditView):
    queryset = CdnSite.objects.select_related("cdn_site_role")
    filterset = filters.CdnSiteFilterSet
    table = tables.CdnSiteTable
    form = forms.CdnSiteBulkEditForm


class CdnSiteBulkDeleteView(generic.BulkDeleteView):
    queryset = CdnSite.objects.select_related("cdn_site_role")
    filterset = filters.CdnSiteFilterSet
    table = tables.CdnSiteTable

class CdnSiteChangeLogView(ObjectChangeLogView):
    base_template = "nautobot_akamai_models/cdnsite.html"
    
class RedirectMapContextListView(generic.ObjectListView):
    queryset = RedirectMapContext.objects.all()
    filterset = filters.RedirectMapContextFilterSet
    filterset_form = forms.RedirectMapContextFilterForm
    table = tables.RedirectMapContextTable
    action_buttons = ("add",)


class RedirectMapContextView(generic.ObjectView):
    queryset = RedirectMapContext.objects.all()

    def get_extra_context(self, request, instance):
        # Determine user's preferred output format
        if request.GET.get("format") in ["json", "yaml"]:
            format_ = request.GET.get("format")
            if request.user.is_authenticated:
                request.user.set_config("redirectmapcontext.format", format_, commit=True)
        elif request.user.is_authenticated:
            format_ = request.user.get_config("redirectmapcontext.format", "json")
        else:
            format_ = "json"

        return {
            "format": format_,
        }

    
class RedirectMapContextEditView(generic.ObjectEditView):
    queryset = RedirectMapContext.objects.all()
    model_form = forms.RedirectMapContextForm
    template_name = "nautobot_cdn_models/redirectmapcontext_edit.html"


class RedirectMapContextBulkEditView(generic.BulkEditView):
    queryset = RedirectMapContext.objects.all()
    filterset = filters.RedirectMapContextFilterSet
    table = tables.RedirectMapContextTable
    form = forms.RedirectMapContextBulkEditForm


class RedirectMapContextDeleteView(generic.ObjectDeleteView):
    queryset = RedirectMapContext.objects.all()


class RedirectMapContextBulkDeleteView(generic.BulkDeleteView):
    queryset = RedirectMapContext.objects.all()
    table = tables.RedirectMapContextTable


# define a merger with a custom list merge strategy
list_merger = Merger(
    # pass in a list of tuple, with the "strategy" as the first element and the "type" as the second element
    [
        (list, ["append"]),
        (dict, ["merge"])
    ],
    ["override"],
    ["override"]
)

class ObjectRedirectMapContextView(generic.ObjectView):
    base_template = None
    template_name = "nautobot_cdn_models/object_redirectmapcontext.html"

    def get_extra_context(self, request, instance):
        source_contexts = RedirectMapContext.objects.restrict(request.user, "view").get_for_object(instance)
        # Merge the context data
        merged_data = {}
        for context in source_contexts:
            merged_data = list_merger.merge(merged_data, context.data)

        # Determine user's preferred output format
        if request.GET.get("format") in ["json", "yaml"]:
            format_ = request.GET.get("format")
            if request.user.is_authenticated:
                request.user.set_config("redirectmapcontext.format", format_, commit=True)
        elif request.user.is_authenticated:
            format_ = request.user.get_config("redirectmapcontext.format", "json")
        else:
            format_ = "json"

        return {
            "rendered_context": merged_data,  # return the merged data instead
            "source_contexts": source_contexts,
            "format": format_,
            "base_template": self.base_template,
            "active_tab": "config-context",
        }

class CdnSiteRedirectMapContextView(ObjectRedirectMapContextView):
    queryset = CdnSite.objects.annotate_config_context_data()
    base_template = "nautobot_akamai_models/cdnsite.html"
    
#
# Config context schemas
#

# TODO(Glenn): disallow (or at least warn) user from manually editing config context schemas that
# have an associated owner, such as a Git repository


class RedirectMapContextSchemaListView(generic.ObjectListView):
    queryset = RedirectMapContextSchema.objects.all()
    filterset = filters.RedirectMapContextSchemaFilterSet
    filterset_form = forms.RedirectMapContextSchemaFilterForm
    table = tables.RedirectMapContextSchemaTable
    action_buttons = ("add",)


class RedirectMapContextSchemaView(generic.ObjectView):
    queryset = RedirectMapContextSchema.objects.all()

    def get_extra_context(self, request, instance):
        # Determine user's preferred output format
        if request.GET.get("format") in ["json", "yaml"]:
            format_ = request.GET.get("format")
            if request.user.is_authenticated:
                request.user.set_config("nautobot_cdn_models.redirectmapcontextschema.format", format_, commit=True)
        elif request.user.is_authenticated:
            format_ = request.user.get_config("nautobot_cdn_models.redirectmapcontextschema.format", "json")
        else:
            format_ = "json"

        return {
            "format": format_,
        }


class RedirectMapContextSchemaObjectValidationView(generic.ObjectView):
    """
    This view renders a detail tab that shows tables of objects that utilize the given schema object
    and their validation state.
    """

    queryset = RedirectMapContextSchema.objects.all()
    template_name = "nautobot_cdn_models/redirectmapcontextschema_validation.html"

    def get_extra_context(self, request, instance):
        """
        Reuse the model tables for config context, device, and virtual machine but inject
        the `RedirectMapContextSchemaValidationStateColumn` and an object edit action button.
        """
        # Prep the validator with the schema so it can be reused for all records
        validator = Draft7Validator(instance.data_schema)

        # Config context table
        config_context_table = tables.RedirectMapContextTable(
            data=instance.config_contexts.all(),
            orderable=False,
            extra_columns=[
                (
                    "validation_state",
                    tables.RedirectMapContextSchemaValidationStateColumn(validator, "data", empty_values=()),
                ),
                ("actions", ButtonsColumn(model=RedirectMapContext, buttons=["edit"])),
            ],
        )
        paginate = {
            "paginator_class": EnhancedPaginator,
            "per_page": get_paginate_count(request),
        }
        RequestConfig(request, paginate).configure(config_context_table)

        # CdnSite table
        cdnsite_table = tables.CdnSiteTable(
            data=instance.cdnsites.select_related(
                "location",
                "cdn_site_ole",
            ),
            orderable=False,
            extra_columns=[
                (
                    "validation_state",
                    tables.RedirectMapContextSchemaValidationStateColumn(
                        validator, "local_config_context_data", empty_values=()
                    ),
                ),
                ("actions", ButtonsColumn(model=CdnSite, buttons=["edit"])),
            ],
        )
        paginate = {
            "paginator_class": EnhancedPaginator,
            "per_page": get_paginate_count(request),
        }
        RequestConfig(request, paginate).configure(cdnsite_table)


class RedirectMapContextSchemaEditView(generic.ObjectEditView):
    queryset = RedirectMapContextSchema.objects.all()
    model_form = forms.RedirectMapContextSchemaForm
    template_name = "nautobot_cdn_models/redirectmapcontextschema_edit.html"


class RedirectMapContextSchemaBulkEditView(generic.BulkEditView):
    queryset = RedirectMapContextSchema.objects.all()
    filterset = filters.RedirectMapContextSchemaFilterSet
    table = tables.RedirectMapContextSchemaTable
    form = forms.RedirectMapContextSchemaBulkEditForm


class RedirectMapContextSchemaDeleteView(generic.ObjectDeleteView):
    queryset = RedirectMapContextSchema.objects.all()


class RedirectMapContextSchemaBulkDeleteView(generic.BulkDeleteView):
    queryset = RedirectMapContextSchema.objects.all()
    table = tables.RedirectMapContextSchemaTable
    filterset = filters.RedirectMapContextSchemaFilterSet
    
#
# Git repositories
#


class CdnGitRepositoryListView(generic.ObjectListView):
    queryset = CdnGitRepository.objects.all()
    filterset = filters.CdnGitRepositoryFilterSet
    filterset_form = forms.CdnGitRepositoryFilterForm
    table = tables.CdnGitRepositoryTable
    template_name = "nautobot_cdn_models/cdngitrepository_list.html"

    def extra_context(self):
        # Get the newest results for each repository name
        results = {
            r.task_kwargs["repository"]: r
            for r in JobResult.objects.filter(
                task_name__startswith="nautobot.core.jobs.GitRepository",
                task_kwargs__repository__isnull=False,
                status__in=JobResultStatusChoices.READY_STATES,
            )
            .order_by("date_done")
            .defer("result")
        }
        return {
            "job_results": results,
            "datasource_contents": get_datasource_contents("nautobot_cdn_models.cdngitrepository"),
        }


class CdnGitRepositoryView(generic.ObjectView):
    queryset = CdnGitRepository.objects.all()

    def get_extra_context(self, request, instance):
        return {
            "datasource_contents": get_datasource_contents("nautobot_cdn_models.cdngitrepository"),
        }


class CdnGitRepositoryEditView(generic.ObjectEditView):
    queryset = CdnGitRepository.objects.all()
    model_form = forms.CdnGitRepositoryForm
    template_name = "nautobot_cdn_models/cdngitrepository_object_edit.html"

    # TODO(jathan): Align with changes for v2 where we're not stashing the user on the instance for
    # magical calls and instead discretely calling `repo.sync(user=user, dry_run=dry_run)`, but
    # again, this will be moved to the API calls, so just something to keep in mind.
    def alter_obj(self, obj, request, url_args, url_kwargs):
        # A CdnGitRepository needs to know the originating request when it's saved so that it can enqueue using it
        obj.user = request.user
        return super().alter_obj(obj, request, url_args, url_kwargs)

    def get_return_url(self, request, obj):
        if request.method == "POST":
            return reverse("extras:gitrepository_result", kwargs={"pk": obj.pk})
        return super().get_return_url(request, obj)


class CdnGitRepositoryDeleteView(generic.ObjectDeleteView):
    queryset = CdnGitRepository.objects.all()


class CdnGitRepositoryBulkImportView(generic.BulkImportView):
    queryset = CdnGitRepository.objects.all()
    table = tables.CdnGitRepositoryBulkTable


class CdnGitRepositoryBulkEditView(generic.BulkEditView):
    queryset = CdnGitRepository.objects.select_related("secrets_group")
    filterset = filters.CdnGitRepositoryFilterSet
    table = tables.CdnGitRepositoryBulkTable
    form = forms.CdnGitRepositoryBulkEditForm

    def alter_obj(self, obj, request, url_args, url_kwargs):
        # A CdnGitRepository needs to know the originating request when it's saved so that it can enqueue using it
        obj.request = request
        return super().alter_obj(obj, request, url_args, url_kwargs)

    def extra_context(self):
        return {
            "datasource_contents": get_datasource_contents("nautobot_cdn_models.cdngitrepository"),
        }


class CdnGitRepositoryBulkDeleteView(generic.BulkDeleteView):
    queryset = CdnGitRepository.objects.all()
    table = tables.CdnGitRepositoryBulkTable
    filterset = filters.CdnGitRepositoryFilterSet

    def extra_context(self):
        return {
            "datasource_contents": get_datasource_contents("nautobot_cdn_models.cdngitrepository"),
        }


def check_and_call_git_repository_function(request, pk, func):
    """Helper for checking Git permissions and worker availability, then calling provided function if all is well
    Args:
        request (HttpRequest): request object.
        pk (UUID): CdnGitRepository pk value.
        func (function): Enqueue git repo function.
    Returns:
        (Union[HttpResponseForbidden,redirect]): HttpResponseForbidden if user does not have permission to run the job,
            otherwise redirect to the job result page.
    """
    if not request.user.has_perm("extras.change_gitrepository"):
        return HttpResponseForbidden()

    # Allow execution only if a worker process is running.
    if not get_worker_count():
        messages.error(request, "Unable to run job: Celery worker process not running.")
    else:
        repository = get_object_or_404(CdnGitRepository, pk=pk)
        job_result = func(repository, request.user)

    return redirect(job_result.get_absolute_url())


class CdnGitRepositorySyncView(View):
    def post(self, request, pk):
        return check_and_call_git_repository_function(request, pk, enqueue_pull_git_repository_and_refresh_data)


class CdnGitRepositoryDryRunView(View):
    def post(self, request, pk):
        return check_and_call_git_repository_function(request, pk, enqueue_git_repository_diff_origin_and_local)


class CdnGitRepositoryResultView(generic.ObjectView):
    """
    Display a JobResult and its Job data.
    """

    queryset = CdnGitRepository.objects.all()
    template_name = "nautobot_cdn_models/cdngitrepository_result.html"

    def get_required_permission(self):
        return "extras.view_gitrepository"

    def get_extra_context(self, request, instance):
        job_result = instance.get_latest_sync()

        return {
            "result": job_result,
            "base_template": "nautobot_cdn_models/cdngitrepository.html",
            "object": instance,
            "active_tab": "result",
        }