from netbox.plugins import PluginMenu, PluginMenuItem, PluginMenuButton

menu = PluginMenu(
    label='Mobility',
    icon_class="mdi mdi-sitemap",
    groups=(
        ('Phone Numbers',
            (
                PluginMenuItem(link="plugins:phone_management_plugin:phonenumberrange_list", link_text="Phone Numbers Range", permissions=["phone_management_plugin.view_site"]),
                PluginMenuItem(link="plugins:phone_management_plugin:phonenumber_list", link_text="Phone Numbers", permissions=["phone_management_plugin.view_site"]),
            ),
        ),
        ('SIM Cards', 
            (
                PluginMenuItem(link="plugins:phone_management_plugin:sim_list", link_text="SIMs", permissions=["phone_management_plugin.view_sim"]),
                PluginMenuItem(link="plugins:phone_management_plugin:simadmin_list", link_text="SIM Private", permissions=["phone_management_plugin.view_simadmin"]),
            ),
        )
    )
)