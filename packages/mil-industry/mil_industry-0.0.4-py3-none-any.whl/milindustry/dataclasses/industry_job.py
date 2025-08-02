
from dataclasses import dataclass
from typing import List, Callable
from datetime import datetime

from eveuniverse.models import (
    EveIndustryActivity,
    EveType,
)

from ..providers import esi

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)


@dataclass
class IndustryJob:
    job_id: int
    activity_id: int
    activity: str
    product_type_id: int
    product_name: str
    runs: int
    start_date: datetime
    installer_id: int
    installer_name: str
    status: str
    completion_date: datetime

    def resolve_type_id(type_id: int) -> str:
        try:
            return EveType.objects.get(id=type_id).name
        except EveType.DoesNotExist:
            return f"Unknown - Type ID: {type_id}"
        
    def resolve_activity_id(type_id: int) -> str:
        try:
            return EveIndustryActivity.objects.get(id=type_id).name
        except EveType.DoesNotExist:
            return f"Unknown - Type ID: {type_id}"

    def convert_from_esi_response(
        esi_jobs: List[dict],
        resolve_type_id: Callable[[int], str],
        resolve_activity_id: Callable[[int], str]
    ):
        jobs: List[IndustryJob] = []

        installer_ids = list({job['installer_id'] for job in esi_jobs})

        if installer_ids:
            character_mapping = {
                entry["id"]: entry["name"]
                for entry in esi.client.Universe.post_universe_names(ids=installer_ids).results()
            }
        else:
            character_mapping = {}

        for job in esi_jobs:
            jobs.append(IndustryJob(
                job_id=job['job_id'],
                activity_id=job['activity_id'],
                activity=resolve_activity_id(job['activity_id']),
                product_type_id=job['product_type_id'],
                product_name=resolve_type_id(job['product_type_id']),
                runs=job['runs'],
                start_date=job['start_date'],
                installer_id=job['installer_id'],
                installer_name=character_mapping.get(job['installer_id']),
                status=job['status'],
                completion_date=job['end_date']
            ))
        
        return jobs