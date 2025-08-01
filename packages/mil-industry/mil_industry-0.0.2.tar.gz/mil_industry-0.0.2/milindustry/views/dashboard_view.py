"""App Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect

from esi.decorators import tokens_required, token_required
from esi.models import Token

from allianceauth.eveonline.models import EveCharacter

from ..models import General
from ..providers import esi
from ..services.jobs_service import (
    get_all_jobs_for_user
)
from..dataclasses.industry_job import IndustryJob

from allianceauth.services.hooks import get_extension_logger
logger = get_extension_logger(__name__)


@login_required
@permission_required("milindustry.basic_access")
@tokens_required(scopes=General.get_esi_scopes())
def jobs_overview(request: WSGIRequest, tokens) -> HttpResponse:
    industry_jobs = get_all_jobs_for_user(tokens=tokens)

    context = {
        "industry_jobs" : sorted(industry_jobs, key=lambda job: job.job_id, reverse=False),
    }
    return render(request, "milindustry/overview.html", context)


@login_required
@permission_required("milindustry.basic_access")
@token_required(scopes=General.get_esi_scopes())
def add_character(request, token) -> HttpResponse:
    logger.info(f"Token for {token.character_name} has been added")

    return redirect("milindustry:jobs_overview")