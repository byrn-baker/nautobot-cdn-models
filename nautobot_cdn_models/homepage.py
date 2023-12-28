from django.contrib.contenttypes.models import ContentType
from django.db.models import F

from nautobot.core.apps import HomePageGroup, HomePageItem, HomePagePanel
from .models import (
    HyperCacheMemoryProfile,
    SiteRole,
    CdnSite
)

layout = (
    HomePagePanel(
        name="Akamai LCDN",
        weight=100,
        items=(
            HomePageItem(
                name="Akamai HyperCache Memory Profiles",
                link="plugins:nautobot_cdn_models:hypercachememoryprofile_list",
                model=HyperCacheMemoryProfile,
                description="Akamai Site Hypercache Memory Profiles",
                permissions=[],
                weight=100,
            ),
            HomePageItem(
                name="Akamai Site Roles",
                link="plugins:nautobot_cdn_models:siterole_list",
                model=SiteRole,
                description="Akamai LCDN Site Groupings",
                permissions=[],
                weight=150,
            ),
            HomePageItem(
                name="Akamai Site Configuration",
                link="plugins:nautobot_cdn_models:cdnsite_list",
                model=CdnSite,
                description="Akamai Site Configuration Source of Truth",
                permissions=[],
                weight=200,
            ),
        ),
    ),
)