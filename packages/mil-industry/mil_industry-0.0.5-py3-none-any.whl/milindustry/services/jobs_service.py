# Django
from typing import List
from esi.models import Token

from ..providers import esi
from ..dataclasses.industry_job import IndustryJob
from ..models.industry_character import IndustryCharacter
from ..models.general import General

from allianceauth.services.hooks import get_extension_logger
logger = get_extension_logger(__name__)


def fetch_jobs_for_character(character: IndustryCharacter) -> List:
    logger.info(f"Fetching jobs for character {character})")

    token = (
        Token.objects.prefetch_related("scopes")
        .filter(character_id=character.eve_character.character_id)
        .require_scopes(General.get_esi_scopes())
        .require_valid()
        .first()
    )

    if not token:
        return []

    personal_jobs = esi.client.Industry.get_characters_character_id_industry_jobs(
        character_id = character.eve_character.character_id,
        token=token.valid_access_token()
    ).results()

    corporation_jobs = []
    try:
        corporation_jobs = esi.client.Industry.get_corporations_corporation_id_industry_jobs(
            corporation_id = character.eve_character.corporation_id,
            token=token.valid_access_token()
        ).results()
    except Exception as e:
        if hasattr(e, "response") and getattr(e.response, "status_code", None) == 403:
            logger.info(f"The character {character.eve_character.character_name} cannot read the corporation jobs - Skipping")
        else:
            raise

    own_corporation_jobs = [
        job for job in corporation_jobs
        if job['installer_id'] == character.eve_character.character_id
    ]

    return personal_jobs + own_corporation_jobs


def get_all_jobs_for_user(characters: List[IndustryCharacter]):
    all_jobs = []

    for character in characters:
        jobs = fetch_jobs_for_character(character)
        all_jobs.extend(jobs)

    return IndustryJob.convert_from_esi_response(
        all_jobs,
        IndustryJob.resolve_type_id,
        IndustryJob.resolve_activity_id
    )
