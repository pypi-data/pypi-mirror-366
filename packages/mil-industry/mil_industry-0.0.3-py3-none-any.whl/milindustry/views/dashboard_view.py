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
from ..services.jobs_service import (
    get_all_jobs_for_user
)
from..helpers import fetch_tokens_for_user

from allianceauth.services.hooks import get_extension_logger
logger = get_extension_logger(__name__)


@login_required
@permission_required("milindustry.basic_access")
def jobs_overview(request: WSGIRequest) -> HttpResponse:
    tokens = fetch_tokens_for_user(user=request.user, scopes=General.get_esi_scopes())

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