from nautobot.core.apps import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuImportButton, NavMenuTab
menu_items = (
    NavMenuTab(
        name="Akamai LCDN",
        weight=100,
        groups=(
            NavMenuGroup(
                name="Akamai Site Configurations",
                weight=100,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_cdn_models:hypercachememoryprofile_list",
                        name="HyperCache Memory Profiles",
                        permissions=[],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_cdn_models:hypercachememoryprofile_add",
                                permissions=[],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_cdn_models:hypercachememoryprofile_import",
                                permissions=[],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_cdn_models:siterole_list",
                        name="Akamai Site Roles",
                        permissions=[],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_cdn_models:siterole_add",
                                permissions=[],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_cdn_models:siterole_import",
                                permissions=[],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_cdn_models:cdnsite_list",
                        name="Akamai Site Configuration",
                        permissions=[],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_cdn_models:cdnsite_add",
                                permissions=[],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_cdn_models:cdnsite_import",
                                permissions=[],
                            ),
                        ),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Redirect Maps",
                weight=200,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_cdn_models:redirectmapcontext_list",
                        name="Redirect Map Contexts",
                        permissions=[],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_cdn_models:redirectmapcontext_add",
                                permissions=[],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
)