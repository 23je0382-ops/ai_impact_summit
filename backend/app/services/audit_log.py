
"""
Audit Log Service

Maintains a comprehensive audit trail of every automated action taken on behalf of the user.
Logs data snapshots, AI generations, verification results, and submission attempts.
"""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.logging_config import get_logger

logger = get_logger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent / "data"
AUDIT_FILE = DATA_DIR / "audit_logs.json"

_audit_lock = threading.RLock()

def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def _read_logs() -> Dict[str, List[Dict[str, Any]]]:
    """Reads logs, returns dict keyed by app_id."""
    try:
        if AUDIT_FILE.exists():
            with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error reading audit logs: {e}")
        return {}

def _write_logs(logs: Dict[str, List[Dict[str, Any]]]) -> bool:
    try:
        _ensure_data_dir()
        temp_path = AUDIT_FILE.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, default=str)
        temp_path.replace(AUDIT_FILE)
        return True
    except Exception as e:
        logger.error(f"Error writing audit logs: {e}")
        return False

def log_audit_event(
    job_id: str,
    event_type: str,
    details: Dict[str, Any],
    step_name: str = "general"
) -> None:
    """
    Log a distinct event in the application process.
    
    Args:
        job_id: The Job ID this event relates to.
        event_type: Category (e.g., 'snapshot', 'generation', 'verification', 'policy', 'submission').
        details: arbitrary JSON data.
        step_name: Human readable step name (e.g. "Resume Verification").
    """
    with _audit_lock:
        logs = _read_logs()
        
        if job_id not in logs:
            logs[job_id] = []
            
        entry = {
            "id": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "step": step_name,
            "details": details
        }
        
        logs[job_id].append(entry)
        _write_logs(logs)

def get_audit_trail(job_id: str) -> List[Dict[str, Any]]:
    """Retrieve the full audit trail for a job/application."""
    with _audit_lock:
        logs = _read_logs()
        return logs.get(job_id, [])
