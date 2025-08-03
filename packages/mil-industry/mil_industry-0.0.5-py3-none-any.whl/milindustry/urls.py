"""App URLs"""

# Django
from django.urls import path

# MIL Industry App
from milindustry.views import dashboard_view

app_name: str = "milindustry"

urlpatterns = [
    path("", dashboard_view.dashboard, name="dashboard"),
    path("jobs_overview", dashboard_view.jobs_overview, name="jobs_overview"),
    path("add_character", dashboard_view.add_character, name="add_character"),
    path("refresh_job_slots_usage", dashboard_view.refresh_job_slots_usage, name="refresh_job_slots_usage"),
]
