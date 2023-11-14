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
        key="cdnsite_devices",
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
        key="cdnsite_vms",
        defaults={
            "label": "CdnSite's Associated VirtualMachines",
            "type": RelationshipTypeChoices.TYPE_MANY_TO_MANY,
            "source_type": ContentType.objects.get_for_model(VirtualMachine),
            "source_label": "VMs associated with a CdnSite",
            "destination_type": ContentType.objects.get_for_model(CdnSite),
            "destination_label": "CdnSite to associated VMs",
        },
    )
