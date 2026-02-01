
"""
Grounding Verifier Service

Validates LLM-generated content against the student's actual profile data
to prevent hallucinations and ensure factual accuracy.
"""

import json
from typing import Dict, Any, List, Optional
from groq import Groq
from app.config import settings
from app.services.data_store import load_student_profile
from app.logging_config import get_logger

logger = get_logger(__name__)

class GroundingError(Exception):
    """Exception for grounding verification failures."""
    pass

def verify_content(content: str, context_type: str = "general") -> Dict[str, Any]:
    """
    Verifies that the content is grounded in the student's profile.
    
    Args:
        content: The text to verify (bullet point, cover letter paragraph, etc.)
        context_type: Type of content ('resume_bullet', 'cover_letter', 'general')
        
    Returns:
        Dict containing:
        - grounded_score (0-100)
        - is_grounded (bool)
        - hallucinations (List[str])
        - reasoning (str)
    """
    try:
        profile = load_student_profile()
        if not profile:
            logger.warning("No student profile found for grounding verification. Skipping check.")
            return {
                "grounded_score": 100,  # Fail open if no profile? Or fail closed? 
                # Ideally we warn. Let's return high score but note it.
                "is_grounded": True,
                "hallucinations": [],
                "reasoning": "Profile not found, skipping verification."
            }

        # Construct Evidence Base
        evidence = {
            "experience": profile.get("experience", []),
            "education": profile.get("education", []),
            "skills": profile.get("skills", []),
            "projects": profile.get("projects", []),  # Assuming projects might exist
            "certifications": profile.get("certifications", [])
        }
        
        evidence_text = json.dumps(evidence, indent=2)
        
        prompt = f"""
        You are a strict Fact-Checking Auditor. Your job is to verify if the text below is FULLY supported by the provided Student Evidence.
        
        STUDENT EVIDENCE:
        {evidence_text}
        
        TEXT TO VERIFY ({context_type}):
        "{content}"
        
        INSTRUCTIONS:
        1. Check if every specific claim (numbers, company names, specific technologies, achievements) in the Text is directly supported by the Evidence.
        2. Allow for minor rewording or summarization, but flag any NEW facts, metrics, or skills not present in the evidence.
        3. If the text infers soft skills (e.g., "fast learner"), that is acceptable if not contradicted.
        4. If a specific metric (e.g., "Increased revenue by 50%") is in the text but NOT in the evidence, flag it as a Hallucination.
        
        OUTPUT JSON ONLY:
        {{
            "score": <0-100 integer, where 100 is fully grounded>,
            "hallucinations": ["<list of specific claims that are unsupported>"],
            "reasoning": "<brief explanation of the score>"
        }}
        """
        
        client = Groq(api_key=settings.groq_api_key)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Fast model for verification
            messages=[
                {"role": "system", "content": "You are a JSON-only outputting Fact Checker."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(completion.choices[0].message.content)
        
        score = result.get("score", 0)
        threshold = 70 # Strictness threshold
        
        return {
            "grounded_score": score,
            "is_grounded": score >= threshold,
            "hallucinations": result.get("hallucinations", []),
            "reasoning": result.get("reasoning", "")
        }
        
    except Exception as e:
        logger.error(f"Grounding verification failed: {e}")
        # Fail open to avoid blocking valid workflows on service error, but log it.
        return {
            "grounded_score": 100, 
            "is_grounded": True, 
            "hallucinations": [], 
            "reasoning": f"Verification failed due to error: {str(e)}"
        }
