from django.contrib.contenttypes.models import ContentType
from django.db.models import F

from nautobot.core.apps import HomePageGroup, HomePageItem, HomePagePanel
from .models import (
    HyperCacheMemoryProfile,
    SiteRole,
    CdnSite,
    CdnConfigContext,
    ServiceProvider,
    ContentProvider,
    Origin,
)

layout = (
    HomePagePanel(
        name="Akamai LCDN",
        weight=100,
        items=(
            HomePageGroup(
                name="Akamai Site Configurations",
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
            HomePageGroup(
                name="Akamai Redirect Map Configurations",
                weight=150,
                items=(
                    HomePageItem(
                        name="Akamai Site Redirect Map Context",
                        link="plugins:nautobot_cdn_models:cdnconfigcontext_list",
                        model=CdnConfigContext,
                        description="Akamai Redirect Map Configuration",
                        permissions=[],
                        weight=250,
                    ),
                ),
            ),
            HomePageGroup(
                name="Akamai Content Delivery Configurations",
                weight=200,
                items=(
                    HomePageItem(
                        name="Akamai Service Providers",
                        link="plugins:nautobot_cdn_models:serviceprovider_list",
                        model=ServiceProvider,
                        description="Akamai Service Prodiver Configuration",
                        permissions=[],
                        weight=300,
                    ),
                    HomePageItem(
                        name="Akamai Content Providers",
                        link="plugins:nautobot_cdn_models:contentprovider_list",
                        model=ContentProvider,
                        description="Akamai Content Prodiver Configuration",
                        permissions=[],
                        weight=350,
                    ),
                    HomePageItem(
                        name="Akamai Origins",
                        link="plugins:nautobot_cdn_models:origin_list",
                        model=Origin,
                        description="Akamai Origin Configuration",
                        permissions=[],
                        weight=400,
                    ),
                ),
            ),
        ),
    ),
)