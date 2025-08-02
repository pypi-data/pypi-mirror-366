from django.core.management import call_command
from django.core.management.base import BaseCommand
from eveuniverse.models import EveType


class Command(BaseCommand):
    help = "Setup all needed data for MIL Industry program to operate"

    def handle(self, *args, **options):
        call_command(
            "eveuniverse_load_data",
            "types",
            "--types-enabled-sections",
            EveType.Section.INDUSTRY_ACTIVITIES,
            EveType.Section.TYPE_MATERIALS,
        )
