# Django
from typing import List
from esi.models import Token

from allianceauth.eveonline.models import EveCharacter

from ..providers import esi
from ..dataclasses.industry_job import IndustryJob

from allianceauth.services.hooks import get_extension_logger
logger = get_extension_logger(__name__)


def fetch_jobs_for_character(token: Token):
    character = EveCharacter.objects.get(character_id=token.character_id)
    logger.info(f"Fetching jobs for character {character.character_name} ({character.character_id})")

    personal_jobs = esi.client.Industry.get_characters_character_id_industry_jobs(
        character_id = character.character_id,
        token=token.valid_access_token()
    ).results()

    corporation_jobs = []
    try:
        corporation_jobs = esi.client.Industry.get_corporations_corporation_id_industry_jobs(
            corporation_id = character.corporation_id,
            token=token.valid_access_token()
        ).results()
    except Exception as e:
        if hasattr(e, "response") and getattr(e.response, "status_code", None) == 403:
            logger.info(f"The character {character.character_name} cannot read the corporation jobs - Skipping")
        else:
            raise

    own_corporation_jobs = [
        job for job in corporation_jobs
        if job['installer_id'] == character.character_id
    ]

    return personal_jobs + own_corporation_jobs


def get_all_jobs_for_user(tokens: List[Token]):
    character_token_map = {}

    for token in tokens:
        if token.character_id not in character_token_map and token.valid_access_token():
            character_token_map[token.character_id] = token

    all_jobs = []
    
    for character_id, token in character_token_map.items():
        jobs = fetch_jobs_for_character(token)
        all_jobs.extend(jobs)

    return IndustryJob.convert_from_esi_response(
        all_jobs,
        IndustryJob.resolve_type_id,
        IndustryJob.resolve_activity_id
    )
