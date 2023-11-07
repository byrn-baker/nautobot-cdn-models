"""Nautobot signal handler functions for nautobot_cdn_models."""
import os
import shutil

from django.apps import apps as global_apps
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from nautobot.extras.choices import RelationshipTypeChoices
from nautobot.core.celery import app

from nautobot.extras.choices import JobResultStatusChoices
from nautobot.extras.models import JobResult

from .models.cdndatasources import CdnGitRepository

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG["nautobot_cdn_models"]

def post_migrate_create_statuses(sender, *, apps=global_apps, **kwargs):
    """Callback function for post_migrate() -- create default Statuses."""
    # pylint: disable=invalid-name
    if not apps:
        return

    Status = apps.get_model("extras", "Status")

    for model_name, default_statuses in PLUGIN_SETTINGS.get("default_statuses", {}).items():
        model = sender.get_model(model_name)

        ContentType = apps.get_model("contenttypes", "ContentType")
        ct_model = ContentType.objects.get_for_model(model)
        for name in default_statuses:
            try:
                status = Status.objects.get(name=name)
            except Status.DoesNotExist:
                print(f"nautobot_cdn_models: Unable to find status: {name} .. SKIPPING")
                continue

            if ct_model not in status.content_types.all():
                status.content_types.add(ct_model)
                status.save()

def create_cdnsite_to_device_relationship(sender, apps, **kwargs):
    """Create a CdnSite-to-Device Relationship if it doesn't already exist."""
    ContentType = apps.get_model("contenttypes", "ContentType")
    Relationship = apps.get_model("extras", "Relationship")
    Device = apps.get_model("dcim", "Device")
    # Use sender.get_model to look up models from this app
    CdnSite = sender.get_model("CdnSite")

    # Ensure that CdnSite to Devices Relationship exists
    Relationship.objects.update_or_create(
        key="cdnsite-devices",
        defaults={
            "label": "CdnSite's Associated Devices",
            "type": RelationshipTypeChoices.TYPE_MANY_TO_MANY,
            "source_type": ContentType.objects.get_for_model(Device),
            "source_label": "Devices associated with a CdnSite",
            "destination_type": ContentType.objects.get_for_model(CdnSite),
            "destination_label": "CdnSite to associated devices",
        },
    )

def create_cdnsite_to_vm_relationship(sender, apps, **kwargs):
    """Create a CdnSite-to-VM Relationship if it doesn't already exist."""
    ContentType = apps.get_model("contenttypes", "ContentType")
    Relationship = apps.get_model("extras", "Relationship")
    VirtualMachine = apps.get_model("virtualization", "VirtualMachine")
    # Use sender.get_model to look up models from this app
    CdnSite = sender.get_model("CdnSite")

    # Ensure that CdnSite to VMs Relationship exists
    Relationship.objects.update_or_create(
        key="cdnsite-vms",
        defaults={
            "label": "CdnSite's Associated VirtualMachines",
            "type": RelationshipTypeChoices.TYPE_MANY_TO_MANY,
            "source_type": ContentType.objects.get_for_model(VirtualMachine),
            "source_label": "VMs associated with a CdnSite",
            "destination_type": ContentType.objects.get_for_model(CdnSite),
            "destination_label": "CdnSite to associated VMs",
        },
    )



#
# Datasources
#


@receiver(pre_delete, sender=CdnGitRepository)
def git_repository_pre_delete(instance, **kwargs):
    """
    When a CdnGitRepository is deleted, invoke all registered callbacks, then remove it from the local filesystem.

    Note that CdnGitRepository create/update operations enqueue a background job to handle the sync/resync;
    this operation, by contrast, happens in the foreground as it needs to complete before we allow the
    CdnGitRepository itself to be deleted.
    """
    from nautobot.extras.datasources import refresh_datasource_content

    # FIXME(jathan): In light of jobs overhaul and Git syncs as jobs, we need to rethink this. We
    # might instead make "delete" another Job class and call it here, but also think about how
    # worker events will be such as firing the worker event here.
    job_result = JobResult.objects.create(
        name=instance.name,
        user=None,
        status=JobResultStatusChoices.STATUS_STARTED,
    )

    # This isn't running in the context of a Job execution transaction,
    # so there's no need to use the "job_logs" proxy DB.
    # In fact, attempting to do so would cause database IntegrityErrors!
    job_result.use_job_logs_db = False

    refresh_datasource_content("plugins.nautobot_cdn_models.cdngitrepository", instance, None, job_result, delete=True)

    # In a distributed Nautobot deployment, each Django instance and/or worker instance may have its own clone
    # of this repository; we need some way to ensure that all such clones are deleted.
    # In the Celery worker case, we can broadcast a control message to all workers to do so:
    app.control.broadcast("discard_git_repository", repository_slug=instance.slug)
    # But we don't have an equivalent way to broadcast to any other Django instances.
    # For now we just delete the one that we have locally and rely on other methods,
    # such as the import_jobs_as_celery_tasks() signal that runs on server startup,
    # to clean up other clones as they're encountered.
    if os.path.isdir(instance.filesystem_path):
        shutil.rmtree(instance.filesystem_path)