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
        name="Akamai SoT",
        weight=100,
        items=(
            HomePageItem(
                name="HyperCache Memory Profiles",
                link="plugins:nautobot_cdn_models:hypercachememoryprofile_list",
                model=HyperCacheMemoryProfile,
                description="Hypercache Memory Profiles",
                permissions=[],
                weight=100,
            ),
            HomePageItem(
                name="Site Roles",
                link="plugins:nautobot_cdn_models:siterole_list",
                model=SiteRole,
                description="CDN Site Roles",
                permissions=[],
                weight=150,
            ),
            HomePageItem(
                name="CDN Sites",
                link="plugins:nautobot_cdn_models:cdnsite_list",
                model=CdnSite,
                description="CDN Sites",
                permissions=[],
                weight=200,
            ),
        ),
    ),
)