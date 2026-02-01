"""Business logic services package."""

from app.services.data_store import (
    # Student Profile
    save_student_profile,
    load_student_profile,
    # Jobs
    save_jobs,
    add_job,
    load_jobs,
    get_job_by_id,
    delete_job,
    # Applications
    save_application,
    update_application,
    load_applications,
    get_application_by_id,
    get_applications_by_status,
    delete_application,
    # Statistics
    get_application_stats,
)

__all__ = [
    # Student Profile
    "save_student_profile",
    "load_student_profile",
    # Jobs
    "save_jobs",
    "add_job",
    "load_jobs",
    "get_job_by_id",
    "delete_job",
    # Applications
    "save_application",
    "update_application",
    "load_applications",
    "get_application_by_id",
    "get_applications_by_status",
    "delete_application",
    # Statistics
    "get_application_stats",
]
