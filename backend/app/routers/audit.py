
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.services.audit_log import get_audit_trail

router = APIRouter(
    prefix="/audit",
    tags=["Audit"]
)

@router.get("/application/{job_id}", response_model=List[Dict[str, Any]])
def get_application_audit(job_id: str):
    """
    Get the complete audit trail for a specific job application.
    """
    logs = get_audit_trail(job_id)
    # Return empty list if no logs, that's valid
    return logs
