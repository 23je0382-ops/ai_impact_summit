"""
Auto Submit Service

Handles the automated submission of application packages to the external Sandbox Portal.
Includes:
- API Client with retries and backoff
- Application status tracking
- Receipt storage
"""

import asyncio
import json
import httpx
from datetime import datetime
from typing import Any, Dict, Optional
import traceback
import random

from app.config import settings
from app.logging_config import get_logger
from app.services.data_store import (
    load_applications, 
    update_application,
    get_job_by_id
)

logger = get_logger(__name__)

# Sandbox URL configuration
# Assuming sandbox is running locally on port 8001 based on user context
SANDBOX_BASE_URL = "http://localhost:8001" 

class SubmissionError(Exception):
    """Base exception for submission errors."""
    pass

async def submit_application(job_id: str) -> Dict[str, Any]:
    """
    Submit the assembled application package for the given job.
    
    1. Find the assembled application record.
    2. Extract the package.
    3. Send to Sandbox API with retries.
    4. Update status (submitted/failed).
    """
    app_record = _find_ready_application(job_id)
    if not app_record:
        raise SubmissionError(f"No assembled application found for job {job_id}")

    # Prepare payload for Sandbox ApplicationForm
    package = app_record.get("application_package", {})
    profile_snap = package.get("profile_snapshot", {})
    artifacts = package.get("artifacts", {})
    
    # Flatten reworded resume into a single string for 'resume_text'
    resume_data = artifacts.get("resume", {})
    resume_lines = []
    if isinstance(resume_data, dict):
        for exp in resume_data.get("experiences", []):
            resume_lines.append(f"--- {exp.get('company')} ---")
            resume_lines.extend(exp.get("tailored_bullets", []))
    resume_text = "\n".join(resume_lines) if resume_lines else str(resume_data)

    payload = {
        "applicant_name": profile_snap.get("name", "Arjun Sharma"),
        "email": profile_snap.get("email", "arjun.iitb@example.com"),
        "phone": profile_snap.get("phone", "+91 98765 43210"),
        "resume_text": resume_text,
        "cover_letter": artifacts.get("cover_letter", ""),
        "linkedin_url": profile_snap.get("linkedin", ""),
        "work_authorization": "US Citizen / OPT",
        "availability": "Immediately",
        "salary_expectation": "Competitive"
    }

    # Sandbox API Endpoint
    url = f"{SANDBOX_BASE_URL}/sandbox/jobs/{job_id}/apply"
    headers = {
        "X-API-Key": "sandbox_demo_key_2026",
        "Content-Type": "application/json"
    }
    
    logger.info(f"Submitting application {app_record['id']} to {url}...")
    
    # Retry Loop
    max_retries = 3
    attempt = 0
    receipt = None
    last_error = None
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        while attempt < max_retries:
            try:
                attempt += 1
                logger.info(f"Submission attempt {attempt}/{max_retries}")
                
                resp = await client.post(url, json=payload, headers=headers)
                
                if resp.status_code in [200, 201]:
                    receipt = resp.json()
                    logger.info("Submission successful!")
                    break
                    
                # Handle Rate Limits
                if resp.status_code == 429:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    logger.warning(f"Rate limited. Waiting {wait_time:.2f}s...")
                    await asyncio.sleep(wait_time)
                    continue
                    
                # Handle Server Errors
                if resp.status_code >= 500:
                    wait_time = 2 ** attempt
                    logger.warning(f"Server error {resp.status_code}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                    
                # Client Errors (4xx) - Do not retry
                resp.raise_for_status()
                
            except httpx.HTTPError as e:
                last_error = str(e)
                wait_time = 2 ** attempt
                logger.warning(f"Network error: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                last_error = str(e)
                break
    
    # Post-Loop Handling
    updates = {
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = {
        "job_id": job_id,
        "application_id": app_record["id"],
        "attempts": attempt,
    }
    
    if receipt:
        updates["status"] = "submitted"
        updates["submitted_at"] = datetime.utcnow().isoformat()
        updates["submission_receipt"] = receipt
        updates["notes"] = app_record.get("notes", "") + f"\nSubmitted successfully on attempt {attempt}."
        
        result["status"] = "success"
        result["receipt"] = receipt
    else:
        updates["status"] = "failed"
        updates["notes"] = app_record.get("notes", "") + f"\nSubmission failed after {attempt} attempts. Error: {last_error}"
        
        result["status"] = "failed"
        result["error"] = last_error
        
    # Persist Status
    update_application(app_record["id"], updates)
    
    if result["status"] == "failed":
        raise SubmissionError(f"Submission failed: {last_error}")
        
    return result

def _find_ready_application(job_id: str) -> Optional[Dict[str, Any]]:
    """Find the latest 'assembled' application for a job."""
    applications = load_applications()
    # Filter for job_id and status='assembled'
    candidates = [
        app for app in applications 
        if app.get("job_id") == job_id and app.get("status") == "assembled"
    ]
    
    if not candidates:
        # Fallback: check 'pending' if it has package data (migrated?)
        candidates = [
            app for app in applications
            if app.get("job_id") == job_id and app.get("application_package")
        ]
        
    if not candidates:
        return None
        
    # Return latest
    return sorted(candidates, key=lambda x: x.get("updated_at", ""), reverse=True)[0]
