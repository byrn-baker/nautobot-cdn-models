from nautobot.core.apps import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuImportButton, NavMenuTab
menu_items = (
    NavMenuTab(
        name="Nautobot Akamai SoT",
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
                        ),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Contexts",
                weight=100,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_cdn_models:cdnconfigcontext_list",
                        name="Contexts",
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
        ),
    ),
)