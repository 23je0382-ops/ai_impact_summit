"""Personalization API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from app.services.resume_tailor import tailor_resume, ResumeTailorError
from app.services.cover_letter import generate_cover_letter, CoverLetterError
from app.services.evidence_mapper import map_evidence, EvidenceMapperError
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/personalize", tags=["Personalize"])

class TailorResumeRequest(BaseModel):
    """Request schema for resume tailoring."""
    job_id: str
    profile_data: Optional[Dict[str, Any]] = None

class TailorResumeResponse(BaseModel):
    """Response schema for tailored resume."""
    tailored_resume: Dict[str, Any]
    changes_log: list[dict]

class GenerateCoverLetterRequest(BaseModel):
    """Request schema for cover letter generation."""
    job_id: str
    profile_data: Optional[Dict[str, Any]] = None

class GenerateCoverLetterResponse(BaseModel):
    """Response schema for cover letter generation."""
    cover_letter_text: str
    context_used: Dict[str, Any]

class MapEvidenceRequest(BaseModel):
    """Request schema for evidence mapping."""
    job_id: str
    profile_data: Optional[Dict[str, Any]] = None

@router.post("/resume", response_model=TailorResumeResponse)
def personalize_resume(request: TailorResumeRequest):
    """
    Generate a tailored resume for a specific job.
    
    1. Matches job requirements to experience bullets
    2. Highlights relevant skills
    3. Rewords content using LLM to mirror job keywords
    """
    try:
        result = tailor_resume(request.job_id, request.profile_data)
        
        return TailorResumeResponse(
            tailored_resume=result,
            changes_log=result.get("meta", {}).get("changes", [])
        )
        
    except ResumeTailorError as e:
        logger.error(f"Tailoring error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error tailoring resume: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/cover-letter", response_model=GenerateCoverLetterResponse)
def create_cover_letter(request: GenerateCoverLetterRequest):
    """
    Generate a personalized 3-paragraph cover letter.
    
    Uses Job Description, Student Profile, Bullet Bank, and Proof Pack
    to construct a compelling narrative.
    """
    try:
        result = generate_cover_letter(request.job_id, request.profile_data)
        
        return GenerateCoverLetterResponse(
            cover_letter_text=result["cover_letter_text"],
            context_used=result["context_used"]
        )
        
    except CoverLetterError as e:
        logger.error(f"Cover letter error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error generating cover letter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/map-evidence", response_model=List[Dict[str, Any]])
def create_evidence_map(request: MapEvidenceRequest):
    """
    Generate a transparent map of job requirements to student evidence.
    
    Returns a table connecting requirements to specific bullets, proof items, or skills.
    "Show me the proof" feature.
    """
    try:
        mapping = map_evidence(request.job_id, request.profile_data)
        return mapping
        
    except EvidenceMapperError as e:
        logger.error(f"Evidence mapping error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error mapping evidence: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
