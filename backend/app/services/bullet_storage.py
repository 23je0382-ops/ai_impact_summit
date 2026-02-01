"""
Bullet Bank Storage Service

Handles storing and retrieving generated achievement bullets.
"""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.logging_config import get_logger

logger = get_logger(__name__)

# Data directory path
DATA_DIR = Path(__file__).parent.parent / "data"
BULLET_BANK_FILE = DATA_DIR / "bullet_bank.json"

# Thread lock for concurrent access
_bullets_lock = threading.RLock()


def _ensure_data_dir() -> None:
    """Ensure the data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_bullet_bank() -> Dict[str, Any]:
    """Read the bullet bank JSON file."""
    try:
        if BULLET_BANK_FILE.exists():
            with open(BULLET_BANK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"bullets": []}
    except Exception as e:
        logger.error(f"Error reading bullet bank file: {e}")
        return {"bullets": []}


def _write_bullet_bank(data: Dict[str, Any]) -> bool:
    """Write to the bullet bank JSON file."""
    try:
        _ensure_data_dir()
        temp_path = BULLET_BANK_FILE.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        temp_path.replace(BULLET_BANK_FILE)
        return True
    except Exception as e:
        logger.error(f"Error writing bullet bank file: {e}")
        return False


def save_bullets(bullets: List[Dict[str, Any]], profile_id: Optional[str] = None) -> bool:
    """
    Save generated bullets to the bullet bank.
    
    Args:
        bullets: List of bullet dictionaries to save.
        profile_id: Optional profile ID to associate bullets with.
        
    Returns:
        True if save was successful.
    """
    with _bullets_lock:
        data = _read_bullet_bank()
        
        # Add profile association and timestamp to each bullet
        for bullet in bullets:
            if profile_id:
                bullet["profile_id"] = profile_id
            bullet["saved_at"] = datetime.utcnow().isoformat()
        
        # Append new bullets
        data["bullets"].extend(bullets)
        
        if _write_bullet_bank(data):
            logger.info(f"Saved {len(bullets)} bullets to bullet bank")
            return True
        return False


def get_all_bullets() -> List[Dict[str, Any]]:
    """Get all bullets from the bullet bank."""
    with _bullets_lock:
        data = _read_bullet_bank()
        return data.get("bullets", [])


def get_bullets_by_category(category: str) -> List[Dict[str, Any]]:
    """Get bullets filtered by category."""
    with _bullets_lock:
        data = _read_bullet_bank()
        bullets = data.get("bullets", [])
        return [b for b in bullets if category in b.get("categories", [])]


def get_bullets_by_source(source_name: str) -> List[Dict[str, Any]]:
    """Get bullets filtered by source name."""
    with _bullets_lock:
        data = _read_bullet_bank()
        bullets = data.get("bullets", [])
        return [
            b for b in bullets 
            if source_name.lower() in b.get("source_name", "").lower()
        ]


def get_bullet_by_id(bullet_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific bullet by ID."""
    with _bullets_lock:
        data = _read_bullet_bank()
        for bullet in data.get("bullets", []):
            if bullet.get("id") == bullet_id:
                return bullet
        return None


def delete_bullet(bullet_id: str) -> bool:
    """Delete a bullet by ID."""
    with _bullets_lock:
        data = _read_bullet_bank()
        original_count = len(data["bullets"])
        data["bullets"] = [b for b in data["bullets"] if b.get("id") != bullet_id]
        
        if len(data["bullets"]) < original_count:
            return _write_bullet_bank(data)
        return False


def clear_all_bullets() -> bool:
    """Clear all bullets from the bullet bank."""
    with _bullets_lock:
        data = {"bullets": []}
        return _write_bullet_bank(data)


def get_bullet_stats() -> Dict[str, Any]:
    """Get statistics about the bullet bank."""
    with _bullets_lock:
        data = _read_bullet_bank()
        bullets = data.get("bullets", [])
        
        # Count by category
        category_counts = {}
        for bullet in bullets:
            for category in bullet.get("categories", []):
                category_counts[category] = category_counts.get(category, 0) + 1
        
        # Count by source type
        source_type_counts = {}
        for bullet in bullets:
            source_type = bullet.get("source_type", "unknown")
            source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1
        
        return {
            "total_bullets": len(bullets),
            "by_category": category_counts,
            "by_source_type": source_type_counts,
            "with_metrics": sum(1 for b in bullets if b.get("has_metrics")),
            "grounded": sum(1 for b in bullets if b.get("is_grounded", True)),
        }
