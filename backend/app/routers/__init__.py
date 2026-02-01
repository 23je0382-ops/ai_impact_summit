"""API routers package."""

from app.routers.health import router as health_router
from app.routers.profile import router as profile_router
from app.routers.jobs import router as jobs_router
from app.routers.applications import router as applications_router
from app.routers.student import router as student_router
from app.routers.personalize import router as personalize_router
from app.routers.policy import router as policy_router
from app.routers.apply import router as apply_router
from app.routers.tracker import router as tracker_router

__all__ = [
    "health_router",
    "profile_router",
    "jobs_router",
    "applications_router",
    "student_router",
    "personalize_router",
    "policy_router",
    "apply_router",
    "tracker_router",
]

