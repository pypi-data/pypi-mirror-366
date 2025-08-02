from celery import shared_task, group

from esi.models import Token

from .models.industry_character import IndustryCharacter
from .models.general import General
from .providers import esi

from allianceauth.services.hooks import get_extension_logger
logger = get_extension_logger(__name__)

TASK_DEFAULT_KWARGS = {"time_limit": 3600, "max_retries": 3}


@shared_task(**{**TASK_DEFAULT_KWARGS, **{"bind": True}})
def update_character_skills(self, industry_character_pk: int):
    new_character = IndustryCharacter.objects.get(pk=industry_character_pk)

    token = (
        Token.objects.prefetch_related("scopes")
        .filter(character_id=new_character.eve_character.character_id)
        .require_scopes(General.get_esi_scopes())
        .require_valid()
        .first()
    )

    if token:
        skills = esi.client.Skills.get_characters_character_id_skills(
            character_id=new_character.eve_character.character_id,
            token=token.valid_access_token(),
        ).results()
        logger.info(f"{len(skills['skills'])} skills retrieved for {new_character}")

        new_character.create_or_update_skills_for_character(
            esi_skills_response=skills,
        )

    else:
        logger.info(f"No valid token for {new_character}")
