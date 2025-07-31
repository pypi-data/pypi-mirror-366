from extras.plugins import PluginConfig

class CVExplorerConfig(PluginConfig):
    name = 'netbox_cvexplorer'
    verbose_name = 'NetBox CVExplorer'
    description = 'Plugin zur Anzeige und Verwaltung von CVE-Informationen'
    version = '1.0.0'
    author = 'Dein Name'
    base_url = 'netbox-cvexplorer'

config = CVExplorerConfig
