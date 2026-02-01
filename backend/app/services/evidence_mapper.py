"""
Evidence Mapper Service

Creates a transparent mapping between job requirements and student evidence.
"""

import json
from typing import Any, Dict, List, Optional
import traceback
import uuid

from app.services.llm_client import generate_json, LLMClientError
from app.logging_config import get_logger
from app.services.data_store import get_job_by_id, load_student_profile
from app.services.job_search import get_stored_jobs
from app.services.bullet_storage import get_all_bullets
from app.services.proof_pack import get_latest_proof_pack

logger = get_logger(__name__)

class EvidenceMapperError(Exception):
    """Base exception for evidence mapping errors."""
    pass

def map_evidence(job_id: str, profile_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Map job requirements to student evidence.
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
            raise EvidenceMapperError(f"Job not found: {job_id}")

        # 2. Fetch Profile (if not provided)
        if not profile_data:
            profile_data = load_student_profile()
            if not profile_data:
                raise EvidenceMapperError("Student profile not found")

        # 3. Fetch Supporting Data
        bullets = get_all_bullets()
        proof_pack = get_latest_proof_pack()
        
        # Prepare context for LLM
        # Only send text to save tokens
        bullet_texts = [b.get("text", "") for b in bullets]
        proof_items = []
        if proof_pack and proof_pack.get("items"):
             proof_items = [
                 f"{item.get('title')} ({item.get('category')}): {item.get('description')} [URL: {item.get('url')}]"
                 for item in proof_pack.get("items")
             ]
             
        student_skills = profile_data.get("skills", [])
        
        # Construct Prompt
        prompt = f"""
        Analyze the job requirements and map them to the student's evidence.
        
        JOB QUALIFICATIONS/REQUIREMENTS:
        {json.dumps(job.get('requirements', []) + job.get('skills_required', []), indent=2)}
        (If generic, infer from Description: {job.get('description')[:500]}...)
        
        STUDENT ARTIFACTS:
        SKILLS: {json.dumps(student_skills)}
        BULLET POINTS (Experience): {json.dumps(bullet_texts, indent=2)}
        PROOF ITEMS (Projects/Links): {json.dumps(proof_items, indent=2)}
        
        TASK:
        For each distinct requirement from the job, find the best matching evidence from the student's artifacts.
        
        Return a JSON array of objects:
        [
          {{
            "requirement": "The specific job requirement",
            "evidence_type": "Skill" | "Bullet" | "Proof" | "None",
            "evidence_content": "The specific matching skill, bullet text, or proof item title",
            "match_strength": "High" | "Medium" | "Low",
            "reasoning": "Why this is a match"
          }}
        ]
        
        Rules:
        1. Prioritize Proof Items and Bullets over just listing a Skill name.
        2. If no direct match, look for transferable skills.
        3. If truly no match, set evidence_type to "None".
        4. Be transparent.
        """
        
        # Call Gemini API via llm_client
        response_text = generate_json(
            prompt=prompt,
            system_prompt="You are a rigorous technical auditor mapping skills to evidence. Return ONLY valid JSON.",
            temperature=0.2
        )
        
        # Extract JSON
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            response_text = json_match.group(1)
            
        try:
            mapping = json.loads(response_text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse mapping JSON: {response_text}")
            mapping = []
            
        # Ensure mapping is a list of dicts
        if not isinstance(mapping, list):
            logger.warning(f"Expected list for mapping, got {type(mapping)}")
            mapping = []
        
        # Add IDs to mapping for UI keys
        validated_mapping = []
        for item in mapping:
            if isinstance(item, dict):
                item["id"] = str(uuid.uuid4())
                validated_mapping.append(item)
            
        return validated_mapping

    except Exception as e:
        logger.error(f"Evidence mapping failed: {traceback.format_exc()}")
        raise EvidenceMapperError(f"Mapping failed: {str(e)}")
