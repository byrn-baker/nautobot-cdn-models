"""Plugin declaration for nautobot_cdn_configuration_manager."""
# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
try:
    from importlib import metadata
except ImportError:
    # Python version < 3.8
    import importlib_metadata as metadata

__version__ = metadata.version(__name__)

from django.db.models.signals import post_migrate
from nautobot.extras.plugins import PluginConfig

class NautobotcdnModelsConfig(PluginConfig):
    """Plugin configuration for the nautobot_cdn_models plugin."""

    name = "nautobot_cdn_models"
    verbose_name = "Nautobot cdn Source of Truth"
    version = __version__
    author = "Byrn Baker"
    description = "Nautobot cdn Soure of Truth."
    base_url = "nautobot-cdn-models"
    required_settings = []
    min_version = "1.2.0"
    max_version = "1.9999"
    default_settings = {
        "default_statuses": {
            "CdnSite": ["active", "maintenance", "planned", "staged", "Decommissioned", "Moved to next phase"],
        }
    }
    caching_config = {}
    def ready(self):
        """Callback invoked after the plugin is loaded."""
        super().ready()

        from .signals import (  # pylint: disable=import-outside-toplevel
            post_migrate_create_statuses,
            create_cdnsite_to_device_relationship,
            create_cdnsite_to_vm_relationship
        )

        post_migrate.connect(post_migrate_create_statuses, sender=self)
        post_migrate.connect(create_cdnsite_to_device_relationship, sender=self)
        post_migrate.connect(create_cdnsite_to_vm_relationship, sender=self)


config = NautobotcdnModelsConfig  # pylint:disable=invalid-name