"""Job Application schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from app.models.job_application import ApplicationStatus


class JobApplicationBase(BaseModel):
    """Base job application schema."""

    company_name: str = Field(..., min_length=1, max_length=255)
    job_title: str = Field(..., min_length=1, max_length=255)
    job_url: Optional[str] = Field(None, max_length=500)
    status: ApplicationStatus = ApplicationStatus.PENDING
    notes: Optional[str] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=255)
    remote: Optional[bool] = False


class JobApplicationCreate(JobApplicationBase):
    """Schema for creating a job application."""

    applied_at: Optional[datetime] = None


class JobApplicationUpdate(BaseModel):
    """Schema for updating a job application."""

    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    job_title: Optional[str] = Field(None, min_length=1, max_length=255)
    job_url: Optional[str] = Field(None, max_length=500)
    status: Optional[ApplicationStatus] = None
    applied_at: Optional[datetime] = None
    notes: Optional[str] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=255)
    remote: Optional[bool] = None


class JobApplicationResponse(JobApplicationBase):
    """Schema for job application response."""

    id: int
    user_id: int
    applied_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobApplicationListResponse(BaseModel):
    """Schema for paginated job application list."""

    items: list[JobApplicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ApplicationStats(BaseModel):
    """Statistics about user's job applications."""

    total: int = 0
    pending: int = 0
    applied: int = 0
    interviewing: int = 0
    offered: int = 0
    rejected: int = 0
    withdrawn: int = 0
