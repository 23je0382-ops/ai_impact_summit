"""
Resume Data Storage Service

Handles storing and retrieving parsed resume data.
"""

import json
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.logging_config import get_logger

logger = get_logger(__name__)

# Data directory path
DATA_DIR = Path(__file__).parent.parent / "data"
RESUMES_FILE = DATA_DIR / "resumes.json"

# Thread lock for concurrent access
_resumes_lock = threading.RLock()


def _ensure_data_dir() -> None:
    """Ensure the data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_resumes_file() -> Dict[str, Any]:
    """Read the resumes JSON file."""
    try:
        if RESUMES_FILE.exists():
            with open(RESUMES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"resumes": []}
    except Exception as e:
        logger.error(f"Error reading resumes file: {e}")
        return {"resumes": []}


def _write_resumes_file(data: Dict[str, Any]) -> bool:
    """Write to the resumes JSON file."""
    try:
        _ensure_data_dir()
        temp_path = RESUMES_FILE.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        temp_path.replace(RESUMES_FILE)
        return True
    except Exception as e:
        logger.error(f"Error writing resumes file: {e}")
        return False


def save_resume_data(
    filename: str,
    extracted_text: str,
    file_size: int,
) -> Optional[Dict[str, Any]]:
    """
    Save parsed resume data to storage.
    
    Args:
        filename: Original filename of the uploaded resume.
        extracted_text: The extracted text content from the PDF.
        file_size: Size of the uploaded file in bytes.
        
    Returns:
        The saved resume record with ID, or None if save failed.
    """
    with _resumes_lock:
        data = _read_resumes_file()
        
        resume_record = {
            "id": str(uuid.uuid4()),
            "filename": filename,
            "extracted_text": extracted_text,
            "file_size": file_size,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        data["resumes"].append(resume_record)
        
        if _write_resumes_file(data):
            logger.info(f"Saved resume data: {resume_record['id']}")
            return resume_record
        
        return None


def get_resume_by_id(resume_id: str) -> Optional[Dict[str, Any]]:
    """Get a resume record by ID."""
    with _resumes_lock:
        data = _read_resumes_file()
        for resume in data["resumes"]:
            if resume.get("id") == resume_id:
                return resume
        return None


def get_all_resumes() -> List[Dict[str, Any]]:
    """Get all resume records."""
    with _resumes_lock:
        data = _read_resumes_file()
        return data.get("resumes", [])


def get_latest_resume() -> Optional[Dict[str, Any]]:
    """Get the most recently uploaded resume."""
    with _resumes_lock:
        data = _read_resumes_file()
        resumes = data.get("resumes", [])
        if resumes:
            return resumes[-1]
        return None


def delete_resume(resume_id: str) -> bool:
    """Delete a resume record by ID."""
    with _resumes_lock:
        data = _read_resumes_file()
        original_count = len(data["resumes"])
        data["resumes"] = [r for r in data["resumes"] if r.get("id") != resume_id]
        
        if len(data["resumes"]) < original_count:
            return _write_resumes_file(data)
        return False
