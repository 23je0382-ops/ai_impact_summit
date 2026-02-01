"""
Proof Pack Service

Extracts and organizes key links/artifacts from a student's profile to create a "Proof Pack".
Uses Groq LLM to generate professional descriptions and map items to relevant skills.
"""

import json
import re
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from groq import Groq

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)

# Data directory path
DATA_DIR = Path(__file__).parent.parent / "data"
PROOF_PACK_FILE = DATA_DIR / "proof_pack.json"

# Thread lock for concurrent access
_proof_lock = threading.RLock()

# Prompt for proof pack generation
PROOF_PACK_PROMPT = """You are a technical career coach. Identify the most impressive artifacts/links from the student's profile and create a "Proof Pack".

STRICT RULES:
1. Extract 3-8 key links/artifacts (GitHub repos, portfolio items, live demos, case studies).
2. For each item, generate a PROFESSIONAL, concise description (1-2 sentences).
3. Map each item to the specific skills or projects it demonstrates.
4. Categorize each item (e.g., "GitHub Repository", "Live Demo", "Portfolio item", "Case Study").
5. Do NOT invent links. Only use links present in the profile.

Return a JSON array of items:
[
  {{
    "title": "Clear name of the artifact/project",
    "url": "Original URL from the profile",
    "category": "Category name",
    "description": "Professional 1-2 sentence description",
    "related_skills": ["List", "of", "demonstrated", "skills"],
    "related_project_name": "Name of the associated project from profile, or null"
  }}
]

Profile Data:
{profile_data}
"""

class ProofPackError(Exception):
    """Exception raised when proof pack generation fails."""
    pass

def _ensure_data_dir() -> None:
    """Ensure the data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def _read_proof_packs() -> Dict[str, Any]:
    """Read the proof pack JSON file."""
    try:
        if PROOF_PACK_FILE.exists():
            with open(PROOF_PACK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"proof_packs": []}
    except Exception as e:
        logger.error(f"Error reading proof pack file: {e}")
        return {"proof_packs": []}

def _write_proof_packs(data: Dict[str, Any]) -> bool:
    """Write to the proof pack JSON file."""
    try:
        _ensure_data_dir()
        temp_path = PROOF_PACK_FILE.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        temp_path.replace(PROOF_PACK_FILE)
        return True
    except Exception as e:
        logger.error(f"Error writing proof pack file: {e}")
        return False

def build_proof_pack_from_profile(profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate a Proof Pack from student profile data using LLM.
    
    Args:
        profile_data: The extracted student profile data.
        
    Returns:
        List of proof items with descriptions and metadata.
        
    Raises:
        ProofPackError: If generation fails.
    """
    if not settings.groq_api_key:
        raise ProofPackError("GROQ_API_KEY not configured")
    
    # Check if there are any links to extract
    has_links = False
    if profile_data.get("links"):
        for val in profile_data["links"].values():
            if val:
                has_links = True
                break
    
    if not has_links and profile_data.get("projects"):
        for proj in profile_data["projects"]:
            # Could look for URLs in descriptions too, but primarily checking explicit project structure if we had one
            # For now, let LLM decide if it can find artifacts in project descriptions/technologies
            has_links = True # Assume LLM might find something
            break
            
    try:
        client = Groq(api_key=settings.groq_api_key)
        
        # Prepare profile for prompt
        profile_for_prompt = {
            k: v for k, v in profile_data.items()
            if not k.startswith("_")
        }
        
        # Call Groq API
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise technical recruiter. Identify and describe proof of work artifacts from the profile. Return ONLY valid JSON array."
                },
                {
                    "role": "user",
                    "content": PROOF_PACK_PROMPT.format(profile_data=json.dumps(profile_for_prompt, indent=2))
                }
            ],
            temperature=0.2,
            max_tokens=2000,
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        # Extract JSON
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            response_text = json_match.group(1)
            
        try:
            items = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Proof Pack JSON: {e}")
            raise ProofPackError("Failed to parse Proof Pack data")
            
        if not isinstance(items, list):
            raise ProofPackError("Expected array of proof items")
            
        # Enrich and validate items
        processed_items = []
        for raw_item in items:
            if not isinstance(raw_item, dict):
                continue
                
            # Normalize keys to lowercase for matching
            norm_item = {k.lower(): v for k, v in raw_item.items()}
            
            # Ensure url is present as that's the core of a proof item
            url = norm_item.get("url") or norm_item.get("link")
            if not url:
                continue
                
            # Build valid ProofItem dict
            processed_item = {
                "id": str(uuid.uuid4()),
                "title": norm_item.get("title") or norm_item.get("name") or "Unnamed Artifact",
                "url": str(url),
                "category": norm_item.get("category") or "General Artifact",
                "description": norm_item.get("description") or "No description provided",
                "related_skills": norm_item.get("related_skills") or [],
                "related_project_name": norm_item.get("related_project_name"),
                "created_at": datetime.utcnow().isoformat(),
            }
            
            # Ensure related_skills is a list
            if not isinstance(processed_item["related_skills"], list):
                if isinstance(processed_item["related_skills"], str):
                    processed_item["related_skills"] = [processed_item["related_skills"]]
                else:
                    processed_item["related_skills"] = []
                    
            processed_items.append(processed_item)
            
        logger.info(f"Built Proof Pack with {len(processed_items)} items")
        return processed_items
        
    except Exception as e:
        logger.error(f"Proof Pack construction failed: {e}")
        raise ProofPackError(f"Generation failed: {str(e)}")

def save_proof_pack(items: List[Dict[str, Any]], profile_id: Optional[str] = None) -> bool:
    """Save a Proof Pack to storage."""
    with _proof_lock:
        data = _read_proof_packs()
        
        pack_record = {
            "id": str(uuid.uuid4()),
            "profile_id": profile_id,
            "created_at": datetime.utcnow().isoformat(),
            "items": items
        }
        
        data["proof_packs"].append(pack_record)
        return _write_proof_packs(data)

def get_latest_proof_pack(profile_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get the most recent Proof Pack."""
    with _proof_lock:
        data = _read_proof_packs()
        packs = data.get("proof_packs", [])
        
        if profile_id:
            packs = [p for p in packs if p.get("profile_id") == profile_id]
            
        if not packs:
            return None
            
        return sorted(packs, key=lambda x: x["created_at"], reverse=True)[0]
