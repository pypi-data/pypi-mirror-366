from celery import shared_task, group

from esi.models import Token

from .models.industry_character import IndustryCharacter
from .models.job_slots_usage import JobSlotsUsage
from .helpers import ActivityType
from .models.general import General
from .providers import esi
from .services.jobs_service import fetch_jobs_for_character

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

    return


@shared_task(**{**TASK_DEFAULT_KWARGS, **{"bind": True}})
def update_all_characters_skills(self):
    all_characters = IndustryCharacter.objects.all()
    
    update_tasks = list()

    for character in all_characters:
        task_signature = update_character_skills.s(industry_character_pk = character.pk)
        update_tasks.append(task_signature)

    group(update_tasks).apply_async(priority=7)


@shared_task(**{**TASK_DEFAULT_KWARGS, **{"bind": True}})
def update_character_slots_usage(self, industry_character_pk: int):
    character = IndustryCharacter.objects.get(pk=industry_character_pk)

    jobs = fetch_jobs_for_character(character=character)

    used_manufacturing = len([
        job for job in jobs if job.get("activity_id") in ActivityType.manufacturing_activities
    ])
    used_reaction = len([
        job for job in jobs if job.get("activity_id") in ActivityType.reaction_activities
    ])
    used_research = len([
        job for job in jobs if job.get("activity_id") in ActivityType.research_activities
    ])

    JobSlotsUsage.objects.update_or_create(
        industry_character=character,
        defaults={
            "manufacturing_used": used_manufacturing,
            "reaction_used": used_reaction,
            "research_used": used_research,
        }
    )

    return


@shared_task(**{**TASK_DEFAULT_KWARGS, **{"bind": True}})
def update_all_characters_slots_usage(self):
    all_characters = IndustryCharacter.objects.all()

    update_tasks = list()

    for character in all_characters:
        task_signature = update_character_slots_usage.s(industry_character_pk = character.pk)
        update_tasks.append(task_signature)

    group(update_tasks).apply_async(priority=7)