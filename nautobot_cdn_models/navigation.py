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
                        name="Akamai Sites Configuration",
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
                name="Akamai Redirect Maps",
                weight=150,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_cdn_models:cdnconfigcontext_list",
                        name="Redirect Map Contexts",
                        permissions=[],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_cdn_models:cdnconfigcontext_add",
                                permissions=[],
                            ),
                        ),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Akamai Content Delivery",
                weight=200,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_cdn_models:serviceprovider_list",
                        name="Service Providers",
                        permissions=[],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_cdn_models:serviceprovider_add",
                                permissions=[],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_cdn_models:contentprovider_list",
                        name="Content Providers",
                        permissions=[],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_cdn_models:contentprovider_add",
                                permissions=[],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_cdn_models:origin_list",
                        name="Origins",
                        permissions=[],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_cdn_models:origin_add",
                                permissions=[],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
)