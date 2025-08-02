from django.dispatch import receiver
from django.db.models.signals import post_save
from .models.industry_character import IndustryCharacter

from milindustry.tasks import update_character_skills

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)

@receiver(post_save, sender=IndustryCharacter)
def on_character_created(sender, instance, created, **kwargs):
    logger.info(f"New Industry character added: {instance.eve_character.character_name} - Refreshing all data")
    if created:
        update_character_skills.delay(
            industry_character_pk=instance.pk,
        )