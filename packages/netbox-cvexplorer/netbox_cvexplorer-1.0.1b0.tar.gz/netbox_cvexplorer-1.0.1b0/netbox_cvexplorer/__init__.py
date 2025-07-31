from netbox.plugins import PluginConfig

__version__ = "1.0.0"

class CVExplorerConfig(PluginConfig):
    name = "netbox_cvexplorer"
    verbose_name = "CVExplorer"
    description = "NetBox plugin to make CVE Documentation."
    version = __version__
    base_url = "cvexplorer"
    author = "Tino Schiffel"
    required_settings = []
    default_settings = {
        "top_level_menu": True,
    }
    min_version = "4.3.0"
    max_version = "4.3.99"


config = CVExplorerConfig
default_app_config = "netbox_cvexplorer.plugin.NetBoxCVExplorerConfig"