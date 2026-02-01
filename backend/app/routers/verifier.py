
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.services.grounding_verifier import verify_content

router = APIRouter(
    prefix="/verify",
    tags=["verification"]
)

class VerifyRequest(BaseModel):
    content: str
    context_type: str = "general"

class VerifyResponse(BaseModel):
    grounded_score: int
    is_grounded: bool
    hallucinations: List[str]
    reasoning: str

@router.post("/grounding", response_model=VerifyResponse)
def verify_grounding(request: VerifyRequest):
    """
    Verify if the provided content is grounded in the student's profile.
    Returns a score and list of potential hallucinations.
    """
    result = verify_content(request.content, request.context_type)
    return result
