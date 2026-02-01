"""Tracker API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from app.services.tracker import (
    get_tracker_summary,
    get_filtered_applications,
    get_failed_applications,
    retry_application,
    TrackerError
)
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/tracker", tags=["Tracker"])

class RetryRequest(BaseModel):
    """Request schema for retrying an application."""
    application_id: str

@router.get("/summary", response_model=Dict[str, Any])
def get_summary():
    """Get high-level dashboard metrics."""
    return get_tracker_summary()

@router.get("/applications", response_model=List[Dict[str, Any]])
def list_filtered_applications(
    status: Optional[str] = Query(None, description="Filter by status"),
    company: Optional[str] = Query(None, description="Filter by company name"),
    date_from: Optional[str] = Query(None, description="Start date (ISO8601)"),
    date_to: Optional[str] = Query(None, description="End date (ISO8601)"),
    limit: int = 100
):
    """Get list of applications with filters."""
    return get_filtered_applications(
        status=status,
        company=company,
        date_from=date_from,
        date_to=date_to,
        limit=limit
    )

@router.get("/failures", response_model=List[Dict[str, Any]])
def list_failures():
    """Get all failed applications."""
    return get_failed_applications()

@router.post("/retry", response_model=Dict[str, Any])
async def retry_failed_application(request: RetryRequest):
    """
    Retry a failed application submission.
    Triggers the submission logic again.
    """
    try:
        result = await retry_application(request.application_id)
        return result
        
    except TrackerError as e:
        logger.error(f"Tracker error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error retrying application: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
