"""Pydantic schemas package."""

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    Token,
    TokenData,
)
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
    JobApplicationListResponse,
    ApplicationStats,
)

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "Token",
    "TokenData",
    "JobApplicationCreate",
    "JobApplicationUpdate",
    "JobApplicationResponse",
    "JobApplicationListResponse",
    "ApplicationStats",
]
