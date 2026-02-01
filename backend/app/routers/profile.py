"""Student profile API endpoints."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.services import load_student_profile, save_student_profile
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/profile", tags=["Profile"])


# ============================================================
# Pydantic Schemas
# ============================================================

class Education(BaseModel):
    """Education entry schema."""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    gpa: Optional[float] = None


class Experience(BaseModel):
    """Work experience entry schema."""
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    current: bool = False
    description: Optional[str] = None


class StudentProfileCreate(BaseModel):
    """Schema for creating/updating student profile."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=255)
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    skills: list[str] = []
    education: list[Education] = []
    experience: list[Experience] = []
    certifications: list[str] = []
    languages: list[str] = []
    preferred_job_types: list[str] = []  # full-time, part-time, contract, internship
    preferred_locations: list[str] = []
    remote_preference: Optional[str] = None  # remote, hybrid, onsite, any
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None


class StudentProfileResponse(StudentProfileCreate):
    """Schema for profile response."""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ============================================================
# API Endpoints
# ============================================================

@router.get("", response_model=Optional[StudentProfileResponse])
async def get_profile():
    """
    Get the current student profile.
    
    Returns the student profile if it exists, otherwise returns null.
    """
    profile = load_student_profile()
    if profile is None:
        return None
    return profile


@router.post("", response_model=StudentProfileResponse)
async def create_or_update_profile(profile: StudentProfileCreate):
    """
    Create or update the student profile.
    
    This endpoint will create a new profile if none exists,
    or update the existing profile with the provided data.
    """
    profile_data = profile.model_dump()
    
    # Preserve created_at if updating
    existing = load_student_profile()
    if existing and "created_at" in existing:
        profile_data["created_at"] = existing["created_at"]
    
    success = save_student_profile(profile_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save profile")
    
    # Return the saved profile
    saved_profile = load_student_profile()
    return saved_profile


@router.patch("", response_model=StudentProfileResponse)
async def partial_update_profile(updates: Dict[str, Any]):
    """
    Partially update the student profile.
    
    Only the provided fields will be updated.
    """
    existing = load_student_profile()
    
    if existing is None:
        raise HTTPException(status_code=404, detail="Profile not found. Create one first.")
    
    # Merge updates with existing data
    existing.update(updates)
    
    success = save_student_profile(existing)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update profile")
    
    return load_student_profile()


@router.delete("", status_code=204)
async def delete_profile():
    """
    Delete the student profile.
    """
    success = save_student_profile(None)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete profile")
    
    return None
