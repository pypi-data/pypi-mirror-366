"""
App Models
Create your models in here
"""

# Django
from django.db import models


class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        """Meta definitions"""

        managed = False
        default_permissions = ()
        permissions = (("basic_access", "Can access this app"),)

    @classmethod
    def get_esi_scopes(cls) -> list:
        return [
            "esi-industry.read_character_jobs.v1",
            "esi-industry.read_corporation_jobs.v1",
            "esi-characters.read_blueprints.v1",
            "esi-skills.read_skills.v1",
            "esi-corporations.read_blueprints.v1",
        ]