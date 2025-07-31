from extras.plugins import PluginMenuItem, PluginMenu

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_cvexplorer:cveentry_list',
        link_text='CVE-Einträge',
    ),
    PluginMenuItem(
        link='plugins:netbox_cvexplorer:cvesource_list',
        link_text='CVE-Quellen',
    ),
)

menu = PluginMenu(
    label='CVExplorer',
    items=menu_items
)