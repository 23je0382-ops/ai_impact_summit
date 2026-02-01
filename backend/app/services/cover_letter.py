"""
Cover Letter Generator Service

Generates a personalized 3-paragraph cover letter using:
1. Job Description (for context)
2. Bullet Bank (for relevant experience)
3. Proof Pack (for evidence)
4. Answer Library (for logistics/CTA)
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
import traceback

from app.services.llm_client import generate_text, LLMClientError
from app.logging_config import get_logger
from app.services.data_store import get_job_by_id, load_student_profile
from app.services.job_search import get_stored_jobs
from app.services.bullet_storage import get_all_bullets
from app.services.proof_pack import get_latest_proof_pack
from app.services.answer_library import get_all_answers, get_answer_by_category
from app.services.grounding_verifier import verify_content

logger = get_logger(__name__)

class CoverLetterError(Exception):
    """Base exception for cover letter generation errors."""
    pass

def generate_cover_letter(job_id: str, profile_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate a personalized cover letter.
    """
    try:
        # 1. Fetch Job
        job = get_job_by_id(job_id)
        if not job:
            search_jobs = get_stored_jobs(limit=1000)
            for j in search_jobs:
                if j.get("id") == job_id:
                    job = j
                    break
        
        if not job:
            raise CoverLetterError(f"Job not found: {job_id}")

        # 2. Fetch Profile (if not provided)
        if not profile_data:
            profile_data = load_student_profile()
            if not profile_data:
                raise CoverLetterError("Student profile not found")

        # 3. Fetch Supporting Data
        bullets = get_all_bullets()
        proof_pack = get_latest_proof_pack()
        answers = get_all_answers()
        
        # Prepare context for LLM
        
        # Relevant Answers (Availability, Relocation, Why Company)
        logistics_context = {}
        relevant_cats = ["availability", "relocation", "why_company"]
        for ans in answers:
            if ans.get("category") in relevant_cats:
                logistics_context[ans.get("category")] = ans.get("answer")
                
        # Proof Items (Top 3)
        proof_items = []
        if proof_pack and proof_pack.get("items"):
             proof_items = proof_pack.get("items")[:3]
             
        # Selected relevant bullets (simple keyword match similar to resume_tailor)
        job_desc = job.get("description", "").lower()
        job_skills = set(s.lower() for s in job.get("skills_required", []))
        
        relevant_bullets = []
        for b in bullets:
            text = b.get("text", "")
            score = 0
            for skill in job_skills:
                if skill in text.lower():
                    score += 1
            if score > 0:
                relevant_bullets.append(text)
        
        # Limit bullets
        relevant_bullets = relevant_bullets[:5]
        
        # Construct Prompt
        prompt = f"""
        Write a professional, enthusiastic 3-paragraph cover letter for a student applying to this job.
        
        JOB DETAILS:
        Title: {job.get('title')}
        Company: {job.get('company')}
        Description: {job.get('description')[:500]}...
        
        STUDENT PROFILE:
        Name: {profile_data.get('name', 'The Candidate')}
        Skills: {', '.join(profile_data.get('skills', [])[:10])}
        
        KEY ACHIEVEMENTS (Use 2-3 of these):
        {json.dumps(relevant_bullets, indent=2)}
        
        PROOF OF WORK (Mention 1 if relevant):
        {json.dumps(proof_items, indent=2)}
        
        LOGISTICS / PREFERENCES:
        {json.dumps(logistics_context, indent=2)}
        
        STRUCTURE:
        Paragraph 1 (Hook): state interest in {job.get('company')} and the {job.get('title')} role. Mention specific excitement about what the company does (infer from description).
        Paragraph 2 (Evidence): Connect specific achievements/bullets to the job requirements. Mention a proof-of-work item if it fits. Prove you can do the job.
        Paragraph 3 (Closing): Reiterate enthusiasm. State availability (from logistics). Call to action (interview request).
        
        TONE: Professional, confident, eager, but not arrogant.
        Start with "Dear Hiring Team," (or specific name if known).
        """
        
        # Call Gemini API via llm_client
        cover_letter_text = generate_text(
            prompt=prompt,
            system_prompt="You are an expert career coach writing a cover letter.",
            temperature=0.7
        )
        
        # Verify Grounding
        verification = verify_content(cover_letter_text, context_type="cover_letter")
        
        return {
            "job_id": job_id,
            "generated_at": datetime.utcnow().isoformat(),
            "cover_letter_text": cover_letter_text,
            "verification": verification,
            "is_grounded": verification.get("is_grounded", False),
            "context_used": {
                "bullet_count": len(relevant_bullets),
                "proof_item_count": len(proof_items),
                "logistics_found": list(logistics_context.keys())
            }
        }

    except Exception as e:
        logger.error(f"Cover letter generation failed: {traceback.format_exc()}")
        raise CoverLetterError(f"Generation failed: {str(e)}")
