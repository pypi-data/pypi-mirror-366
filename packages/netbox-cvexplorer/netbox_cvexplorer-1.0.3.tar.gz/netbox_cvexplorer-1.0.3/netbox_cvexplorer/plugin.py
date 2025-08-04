from netbox.plugins import PluginConfig

class CVExplorerConfig(PluginConfig):
    name = 'netbox_cvexplorer'
    verbose_name = 'CVE Explorer'
    description = 'Zeigt CVE-Daten in NetBox'
    author  = 'Tino Schiffel'
    author_email = 'worker@billhost.de'
    version = '1.0.3'
    base_url = 'cvexplorer'
    required_settings = []
    default_settings = {}

config = CVExplorerConfig
