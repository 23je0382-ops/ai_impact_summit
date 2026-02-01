"""Applications API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services import (
    load_applications,
    save_application,
    update_application,
    get_application_by_id,
    get_applications_by_status,
    delete_application,
    get_application_stats,
    get_job_by_id,
)
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/applications", tags=["Applications"])


# ============================================================
# Pydantic Schemas
# ============================================================

class ApplicationBase(BaseModel):
    """Base application schema."""
    job_id: Optional[str] = None  # Reference to job if exists
    company_name: str = Field(..., min_length=1, max_length=255)
    job_title: str = Field(..., min_length=1, max_length=255)
    job_url: Optional[str] = None
    status: str = "pending"  # pending, applied, interviewing, offered, rejected, withdrawn
    applied_at: Optional[str] = None
    resume_used: Optional[str] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None
    salary_offered: Optional[int] = None
    location: Optional[str] = None
    remote: bool = False
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    next_step: Optional[str] = None
    next_step_date: Optional[str] = None
    tags: list[str] = []


class ApplicationCreate(ApplicationBase):
    """Schema for creating an application."""
    pass


class ApplicationUpdate(BaseModel):
    """Schema for updating an application."""
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    job_title: Optional[str] = Field(None, min_length=1, max_length=255)
    job_url: Optional[str] = None
    status: Optional[str] = None
    applied_at: Optional[str] = None
    resume_used: Optional[str] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None
    salary_offered: Optional[int] = None
    location: Optional[str] = None
    remote: Optional[bool] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    next_step: Optional[str] = None
    next_step_date: Optional[str] = None
    tags: Optional[list[str]] = None


class ApplicationResponse(ApplicationBase):
    """Schema for application response."""
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ApplicationListResponse(BaseModel):
    """Schema for applications list response."""
    applications: List[ApplicationResponse]
    total: int


class ApplicationStatsResponse(BaseModel):
    """Schema for application statistics."""
    total: int
    pending: int
    applied: int
    interviewing: int
    offered: int
    rejected: int
    withdrawn: int


# ============================================================
# API Endpoints
# ============================================================

@router.get("", response_model=ApplicationListResponse)
async def list_applications(
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in company and title"),
    company: Optional[str] = Query(None, description="Filter by company"),
):
    """
    List all applications with optional filtering.
    """
    if status:
        applications = get_applications_by_status(status)
    else:
        applications = load_applications()
    
    # Apply additional filters
    if search:
        search_lower = search.lower()
        applications = [a for a in applications if 
                       search_lower in a.get("company_name", "").lower() or 
                       search_lower in a.get("job_title", "").lower()]
    
    if company:
        applications = [a for a in applications if 
                       company.lower() in a.get("company_name", "").lower()]
    
    # Sort by updated_at descending
    applications.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    
    return ApplicationListResponse(applications=applications, total=len(applications))


@router.get("/stats", response_model=ApplicationStatsResponse)
async def get_stats():
    """
    Get application statistics.
    """
    stats = get_application_stats()
    return stats


@router.post("", response_model=ApplicationResponse, status_code=201)
async def create_application(application: ApplicationCreate):
    """
    Create a new job application.
    """
    app_data = application.model_dump()
    
    # If job_id is provided, fetch job details
    if app_data.get("job_id"):
        job = get_job_by_id(app_data["job_id"])
        if job:
            # Auto-fill from job if not provided
            if not app_data.get("company_name"):
                app_data["company_name"] = job.get("company", "")
            if not app_data.get("job_title"):
                app_data["job_title"] = job.get("title", "")
            if not app_data.get("job_url"):
                app_data["job_url"] = job.get("url", "")
            if not app_data.get("location"):
                app_data["location"] = job.get("location", "")
            if not app_data.get("remote"):
                app_data["remote"] = job.get("remote", False)
    
    app_id = save_application(app_data)
    
    if not app_id:
        raise HTTPException(status_code=500, detail="Failed to create application")
    
    created_app = get_application_by_id(app_id)
    return created_app


@router.get("/{app_id}", response_model=ApplicationResponse)
async def get_application(app_id: str):
    """
    Get a specific application by ID.
    """
    application = get_application_by_id(app_id)
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return application


@router.put("/{app_id}", response_model=ApplicationResponse)
async def update_application_endpoint(app_id: str, app_update: ApplicationUpdate):
    """
    Update an application.
    """
    existing = get_application_by_id(app_id)
    
    if not existing:
        raise HTTPException(status_code=404, detail="Application not found")
    
    update_data = app_update.model_dump(exclude_unset=True)
    
    if not update_application(app_id, update_data):
        raise HTTPException(status_code=500, detail="Failed to update application")
    
    return get_application_by_id(app_id)


@router.patch("/{app_id}/status", response_model=ApplicationResponse)
async def update_status(app_id: str, status: str):
    """
    Update the status of an application.
    
    Valid statuses: pending, applied, interviewing, offered, rejected, withdrawn
    """
    valid_statuses = ["pending", "applied", "interviewing", "offered", "rejected", "withdrawn"]
    
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    existing = get_application_by_id(app_id)
    
    if not existing:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if not update_application(app_id, {"status": status}):
        raise HTTPException(status_code=500, detail="Failed to update status")
    
    return get_application_by_id(app_id)


@router.delete("/{app_id}", status_code=204)
async def remove_application(app_id: str):
    """
    Delete an application.
    """
    if not get_application_by_id(app_id):
        raise HTTPException(status_code=404, detail="Application not found")
    
    if not delete_application(app_id):
        raise HTTPException(status_code=500, detail="Failed to delete application")
    
    return None


@router.post("/from-job/{job_id}", response_model=ApplicationResponse, status_code=201)
async def create_from_job(job_id: str, notes: Optional[str] = None):
    """
    Create an application from an existing job entry.
    """
    job = get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    app_data = {
        "job_id": job_id,
        "company_name": job.get("company", ""),
        "job_title": job.get("title", ""),
        "job_url": job.get("url"),
        "location": job.get("location"),
        "remote": job.get("remote", False),
        "status": "pending",
        "notes": notes,
    }
    
    app_id = save_application(app_data)
    
    if not app_id:
        raise HTTPException(status_code=500, detail="Failed to create application")
    
    return get_application_by_id(app_id)
