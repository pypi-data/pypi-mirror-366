from django.db import models, transaction
from django.db.models import UniqueConstraint
from typing import Dict, List, TypedDict

from esi.models import Token
from eveuniverse.models import EveType
from allianceauth.eveonline.models import EveCharacter

from ..helpers import SkillGroups, ActivityType
from ..dataclasses.slots_overview import CharacterSlotOverview, SlotCategory
from .general import General

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)

class EsiSkill(TypedDict):
    skill_id: int
    active_skill_level: int
    skillpoints_in_skill: int
    trained_skill_level: int

class EsiSkillsData(TypedDict):
    skills: List[EsiSkill]
    total_sp: int
    unallocated_sp: int

class IndustryCharacter(models.Model):
    id = models.AutoField(primary_key=True)
    eve_character = models.OneToOneField(
        EveCharacter, related_name="milindustry_industrycharacter", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.eve_character.character_name} (PK:{self.pk})"

    def __repr__(self) -> str:
        return f"Character(pk={self.pk}, eve_character='{self.eve_character}')"
    
    @classmethod
    @transaction.atomic
    def register_new_character(cls, new_character_id: int):
        from .job_slots_usage import JobSlotsUsage

        new_character = EveCharacter.objects.get(character_id=new_character_id)

        industryCharacter, _ = IndustryCharacter.objects.update_or_create(
            eve_character=new_character,
        )

        jobSlotsUsage, _ = JobSlotsUsage.objects.update_or_create(
            industry_character=industryCharacter,
        )
        
        return
    
    def create_or_update_skills_for_character(self, esi_skills_response: EsiSkillsData) -> None:
        industry_skill_ids = (
            SkillGroups.reaction_slots
            + SkillGroups.manufacturing_slots
            + SkillGroups.research_slots
        )

        skills_to_upsert = [
            IndustryCharacterSkill(
                industry_character=self,
                skill_type_id=skill['skill_id'],
                skill_level=skill['active_skill_level']
            )
            for skill in esi_skills_response['skills']
            if skill['skill_id'] in industry_skill_ids
        ]

        for skill in skills_to_upsert:
            IndustryCharacterSkill.objects.update_or_create(
                industry_character=skill.industry_character,
                skill_type=skill.skill_type,
                defaults={'skill_level': skill.skill_level}
            )
    
    def get_slots_overview(self) -> CharacterSlotOverview:
        from ..services.jobs_service import fetch_jobs_for_character
        # Get all the IndustryCharacterSkill objects for this character, indexed by skill_type_id
        skills = {skill.skill_type_id: skill.skill_level for skill in self.skills.all()}

        def sum_skill_levels(skill_ids):
            return sum(skills.get(skill_id, 0) for skill_id in skill_ids)

        manufacturing_max = 1 + sum_skill_levels(SkillGroups.manufacturing_slots)
        reaction_max = 1 + sum_skill_levels(SkillGroups.reaction_slots)
        research_max = 1 + sum_skill_levels(SkillGroups.research_slots)

        used_manufacturing = self.job_slots_usage.manufacturing_used
        used_reaction = self.job_slots_usage.reaction_used
        used_research = self.job_slots_usage.research_used

        return CharacterSlotOverview(
            character_name=self.eve_character.character_name,
            character_id=self.eve_character.character_id,
            manufacturing = SlotCategory(
                used=used_manufacturing,
                unused=manufacturing_max - used_manufacturing,
                max=manufacturing_max,
                disabled=11 - manufacturing_max,
            ),
            reaction = SlotCategory(
                used=used_reaction,
                unused=reaction_max - used_reaction,
                max=reaction_max,
                disabled=11 - reaction_max,
            ),
            research = SlotCategory(
                used=used_research,
                unused=research_max - used_research,
                max=research_max,
                disabled=11 - research_max,
            ),
            as_of = self.job_slots_usage.last_update
        )

class IndustryCharacterSkill(models.Model):
    industry_character = models.ForeignKey(
        IndustryCharacter,
        related_name='skills',
        on_delete=models.CASCADE
    )
    skill_type = models.ForeignKey(
        EveType,
        related_name='industry_character_skills',
        on_delete=models.CASCADE
    )
    skill_level = models.PositiveSmallIntegerField()  # Skills go from 1 to 5

    class Meta:
        constraints = [
            UniqueConstraint(fields=['industry_character', 'skill_type'], name='unique_industry_character_skill')
        ]

    def __str__(self):
        return f"{self.industry_character} - {self.skill_type} lvl {self.skill_level}"
