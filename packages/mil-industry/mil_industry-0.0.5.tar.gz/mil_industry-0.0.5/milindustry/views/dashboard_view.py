"""App Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.html import format_html

from esi.decorators import tokens_required, token_required
from esi.models import Token

from allianceauth.eveonline.models import EveCharacter
from allianceauth.framework.api.user import get_all_characters_from_user

from ..models import General
from ..services.jobs_service import (
    get_all_jobs_for_user
)
from ..models.industry_character import IndustryCharacter
from ..helpers import fetch_tokens_for_user

from allianceauth.services.hooks import get_extension_logger
logger = get_extension_logger(__name__)


@login_required
@permission_required("milindustry.basic_access")
def dashboard(request: WSGIRequest):
    all_characters = IndustryCharacter.objects.filter(
            eve_character__in=get_all_characters_from_user(user = request.user)
    ).prefetch_related("skills", "eve_character")

    characters_slots_overview = [
        character.get_slots_overview() for character in all_characters
    ]

    aggregated_slots = {
        "manufacturing": {
            "used": sum(char.manufacturing.used for char in characters_slots_overview),
            "max": sum(char.manufacturing.max for char in characters_slots_overview),
        },
        "reaction": {
            "used": sum(char.reaction.used for char in characters_slots_overview),
            "max": sum(char.reaction.max for char in characters_slots_overview),
        },
        "research": {
            "used": sum(char.research.used for char in characters_slots_overview),
            "max": sum(char.research.max for char in characters_slots_overview),
        },
    }

    context = {
        "characters_slots_overview": characters_slots_overview,
        "aggregated_slots": aggregated_slots,
    }

    return render(request, "milindustry/dashboard.html", context)

@login_required
@permission_required("milindustry.basic_access")
def jobs_overview(request: WSGIRequest) -> HttpResponse:
    all_characters = IndustryCharacter.objects.filter(
            eve_character__in=get_all_characters_from_user(user = request.user)
    ).prefetch_related("eve_character")

    industry_jobs = get_all_jobs_for_user(characters=all_characters)

    context = {
        "industry_jobs" : sorted(industry_jobs, key=lambda job: job.job_id, reverse=False),
    }
    return render(request, "milindustry/overview.html", context)


@login_required
@permission_required("milindustry.basic_access")
@token_required(scopes=General.get_esi_scopes())
def add_character(request, token) -> HttpResponse:
    logger.info(f"Token for {token.character_name} has been added")
    IndustryCharacter.register_new_character(
        new_character_id=token.character_id
    )

    messages.success(
        request,
        format_html(
            "<strong>{}</strong> has been registered. It might take a couple of minutes for its data to be updated.",
            token.character_name,
        ),
    )

    return redirect("milindustry:dashboard")


@login_required
@permission_required("milindustry.basic_access")
def refresh_job_slots_usage(request) -> HttpResponse:
    from ..tasks import update_character_slots_usage

    all_characters = IndustryCharacter.objects.filter(
            eve_character__in=get_all_characters_from_user(user = request.user)
    ).prefetch_related("eve_character")

    for character in all_characters:
        update_character_slots_usage.apply_async(
            kwargs={
                "industry_character_pk":character.pk
            },
            priority=5
        )

    messages.success(
        request,
        format_html(
            "A refresh has been requested - It might take a couple of minutes.<br>" \
            "Please reload the page to see the changes",
        ),
    )

    return redirect("milindustry:dashboard")