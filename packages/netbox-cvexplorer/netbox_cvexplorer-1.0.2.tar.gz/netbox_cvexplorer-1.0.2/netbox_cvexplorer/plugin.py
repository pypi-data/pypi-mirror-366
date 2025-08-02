from extras.plugins import PluginConfig

class CVExplorerConfig(PluginConfig):
    name = 'netbox_cvexplorer'
    verbose_name = 'CVE Explorer'
    description = 'Zeigt CVE-Daten in NetBox'
    version = '0.1'
    base_url = 'cvexplorer'
    required_settings = []
    default_settings = {}

config = CVExplorerConfig
