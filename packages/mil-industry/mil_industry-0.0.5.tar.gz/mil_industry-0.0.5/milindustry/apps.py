"""App Configuration"""

# Django
from django.apps import AppConfig

# AA Example App
from milindustry import __version__


class MilindustryConfig(AppConfig):
    """App Config"""

    name = "milindustry"
    label = "milindustry"
    verbose_name = f"MIL Industry v{__version__}"

    def ready(self):
        import milindustry.signals