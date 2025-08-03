from django.db import models, transaction

from ..models.industry_character import IndustryCharacter

class JobSlotsUsage(models.Model):
    industry_character = models.OneToOneField(
        IndustryCharacter,
        primary_key=True,
        related_name="job_slots_usage",
        on_delete=models.CASCADE
    )
    manufacturing_used = models.PositiveSmallIntegerField(default=0)
    reaction_used = models.PositiveSmallIntegerField(default=0)
    research_used = models.PositiveSmallIntegerField(default=0)
    last_update = models.DateTimeField(auto_now=True)
        
    def __str__(self) -> str:
        return f"{self.industry_character}"

    def __repr__(self) -> str:
        return f"IndustryCharacter(pk={self.pk})"