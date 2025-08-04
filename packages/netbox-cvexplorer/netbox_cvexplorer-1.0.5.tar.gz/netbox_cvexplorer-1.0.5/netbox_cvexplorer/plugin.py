from netbox.plugins import PluginConfig
from importlib.metadata import metadata

class CVExplorerConfig(PluginConfig):
    name = 'netbox_cvexplorer'
    verbose_name = 'CVE Explorer'
    description = 'Zeigt CVE-Daten in NetBox'
    author  = 'Tino Schiffel'
    author_email = 'worker@billhost.de'
    version = '1.0.5'
    base_url = 'cvexplorer'
    required_settings = []
    default_settings = {}

config = CVExplorerConfig