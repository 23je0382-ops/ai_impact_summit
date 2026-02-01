"""
Job Search Service

Fetches jobs from the sandbox portal, filters based on student constraints,
deduplicates, and stores unique jobs locally.
"""

import json
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import httpx

from app.logging_config import get_logger

logger = get_logger(__name__)

# Configuration
SANDBOX_PORTAL_URL = "http://localhost:8001"
DATA_DIR = Path(__file__).parent.parent.parent / "data"
JOB_LISTINGS_FILE = DATA_DIR / "job_listings.json"

_jobs_lock = threading.RLock()


def _ensure_data_dir() -> None:
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_job_listings() -> Dict[str, Any]:
    """Read job listings from file."""
    try:
        if JOB_LISTINGS_FILE.exists():
            with open(JOB_LISTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"jobs": [], "seen_hashes": []}
    except Exception as e:
        logger.error(f"Error reading job listings: {e}")
        return {"jobs": [], "seen_hashes": []}


def _write_job_listings(data: Dict[str, Any]) -> bool:
    """Write job listings to file."""
    try:
        _ensure_data_dir()
        with open(JOB_LISTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error writing job listings: {e}")
        return False


def _generate_job_hash(company: str, title: str) -> str:
    """Generate a unique hash for deduplication based on company + title."""
    key = f"{company.lower().strip()}|{title.lower().strip()}"
    return hashlib.md5(key.encode()).hexdigest()


async def fetch_jobs_from_sandbox(
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    is_remote: Optional[bool] = None,
    skill: Optional[str] = None,
    per_page: int = 100,
) -> List[Dict[str, Any]]:
    """
    Fetch jobs from the sandbox portal API.
    
    Args:
        job_type: Filter by job type (internship, full-time)
        experience_level: Filter by experience level (entry, mid, senior)
        is_remote: Filter by remote status
        skill: Filter by skill name
        per_page: Number of jobs per page
        
    Returns:
        List of job postings from sandbox portal
    """
    try:
        params = {"per_page": per_page}
        if job_type:
            params["job_type"] = job_type
        if experience_level:
            params["experience_level"] = experience_level
        if is_remote is not None:
            params["is_remote"] = str(is_remote).lower()
        if skill:
            params["skill"] = skill
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SANDBOX_PORTAL_URL}/sandbox/jobs",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            
            # Fetch full details for each job
            jobs = []
            for job_item in data.get("jobs", []):
                try:
                    detail_response = await client.get(
                        f"{SANDBOX_PORTAL_URL}/sandbox/jobs/{job_item['id']}"
                    )
                    if detail_response.status_code == 200:
                        jobs.append(detail_response.json())
                except Exception as e:
                    logger.warning(f"Failed to fetch job details for {job_item['id']}: {e}")
                    # Use the list item if details fail
                    jobs.append(job_item)
            
            return jobs
            
    except Exception as e:
        logger.error(f"Error fetching jobs from sandbox: {e}")
        return []


def filter_jobs_by_constraints(
    jobs: List[Dict[str, Any]],
    required_skills: Optional[List[str]] = None,
    preferred_locations: Optional[List[str]] = None,
    remote_only: bool = False,
    visa_sponsorship_required: bool = False,
    min_salary: Optional[int] = None,
    experience_levels: Optional[List[str]] = None,
    job_types: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Filter jobs based on student constraints.
    
    Args:
        jobs: List of job postings to filter
        required_skills: Skills the student has (at least one must match)
        preferred_locations: Preferred job locations
        remote_only: Only include remote jobs
        visa_sponsorship_required: Only include jobs that sponsor visas
        min_salary: Minimum salary threshold
        experience_levels: Acceptable experience levels
        job_types: Acceptable job types
        
    Returns:
        Filtered list of job postings
    """
    filtered = []
    
    for job in jobs:
        # Check remote preference
        if remote_only and not job.get("is_remote", False):
            continue
        
        # Check visa sponsorship
        if visa_sponsorship_required and not job.get("visa_sponsorship", False):
            continue
        
        # Check experience level
        if experience_levels:
            job_level = job.get("experience_level", "").lower()
            if job_level and job_level not in [el.lower() for el in experience_levels]:
                continue
        
        # Check job type
        if job_types:
            job_type = job.get("job_type", "").lower()
            if job_type and job_type not in [jt.lower() for jt in job_types]:
                continue
        
        # Check skills match (at least one required skill must match)
        if required_skills:
            job_skills = [s.lower() for s in job.get("skills_required", [])]
            required_lower = [s.lower() for s in required_skills]
            if not any(skill in job_skills for skill in required_lower):
                # Also check partial matches
                partial_match = False
                for req_skill in required_lower:
                    for job_skill in job_skills:
                        if req_skill in job_skill or job_skill in req_skill:
                            partial_match = True
                            break
                    if partial_match:
                        break
                if not partial_match:
                    continue
        
        # Check location preference
        if preferred_locations and not job.get("is_remote", False):
            job_location = job.get("location", "").lower()
            location_match = any(
                loc.lower() in job_location or job_location in loc.lower()
                for loc in preferred_locations
            )
            if not location_match:
                continue
        
        # Check minimum salary (parse salary range)
        if min_salary:
            salary_range = job.get("salary_range", "")
            if salary_range:
                try:
                    # Extract numbers from salary string (e.g., "$120,000-180,000")
                    import re
                    numbers = re.findall(r'[\d,]+', salary_range.replace(',', ''))
                    if numbers:
                        min_job_salary = int(numbers[0].replace(',', ''))
                        # For hourly rates, convert to annual (assuming 40hr/week, 12 weeks intern)
                        if '/hr' in salary_range:
                            min_job_salary = min_job_salary * 40 * 12
                        if min_job_salary < min_salary:
                            continue
                except ValueError:
                    pass  # Can't parse salary, include job anyway
        
        # Calculate a match score for ranking
        match_score = 0
        if required_skills:
            job_skills = [s.lower() for s in job.get("skills_required", [])]
            matched = sum(1 for s in required_skills if s.lower() in job_skills)
            match_score += matched * 10
        
        if job.get("is_remote", False):
            match_score += 5
        
        if job.get("visa_sponsorship", False):
            match_score += 5
        
        job["match_score"] = match_score
        filtered.append(job)
    
    # Sort by match score (highest first)
    filtered.sort(key=lambda j: j.get("match_score", 0), reverse=True)
    
    return filtered


def deduplicate_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate jobs by (company + title).
    
    Args:
        jobs: List of job postings
        
    Returns:
        Deduplicated list of jobs
    """
    seen_hashes: Set[str] = set()
    unique_jobs = []
    
    for job in jobs:
        company = job.get("company", "")
        title = job.get("title", "")
        job_hash = _generate_job_hash(company, title)
        
        if job_hash not in seen_hashes:
            seen_hashes.add(job_hash)
            job["dedup_hash"] = job_hash
            unique_jobs.append(job)
    
    return unique_jobs


def store_jobs(jobs: List[Dict[str, Any]]) -> int:
    """
    Store unique jobs in the job listings table.
    
    Args:
        jobs: List of job postings to store
        
    Returns:
        Number of new jobs added
    """
    with _jobs_lock:
        data = _read_job_listings()
        existing_hashes = set(data.get("seen_hashes", []))
        
        new_jobs = 0
        for job in jobs:
            job_hash = job.get("dedup_hash") or _generate_job_hash(
                job.get("company", ""),
                job.get("title", "")
            )
            
            if job_hash not in existing_hashes:
                existing_hashes.add(job_hash)
                job["stored_at"] = datetime.utcnow().isoformat()
                job["status"] = "new"
                data["jobs"].append(job)
                new_jobs += 1
        
        data["seen_hashes"] = list(existing_hashes)
        _write_job_listings(data)
        
        return new_jobs


def get_stored_jobs(
    status: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Get stored jobs from the listings table.
    
    Args:
        status: Filter by job status (new, applied, saved, rejected)
        limit: Maximum number of jobs to return
        
    Returns:
        List of stored job postings
    """
    with _jobs_lock:
        data = _read_job_listings()
        jobs = data.get("jobs", [])
        
        if status:
            jobs = [j for j in jobs if j.get("status") == status]
        
        return jobs[:limit]


async def search_and_store_jobs(
    required_skills: Optional[List[str]] = None,
    preferred_locations: Optional[List[str]] = None,
    remote_only: bool = False,
    visa_sponsorship_required: bool = False,
    min_salary: Optional[int] = None,
    experience_levels: Optional[List[str]] = None,
    job_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Main function to search, filter, deduplicate, and store jobs.
    
    Args:
        All constraint parameters for filtering
        
    Returns:
        Search result summary with matching jobs
    """
    # Fetch jobs from sandbox
    all_jobs = await fetch_jobs_from_sandbox(per_page=100)
    
    if not all_jobs:
        return {
            "success": False,
            "message": "Failed to fetch jobs from sandbox portal",
            "jobs": [],
            "total_fetched": 0,
            "total_matching": 0,
            "new_jobs_stored": 0,
        }
    
    # Filter by constraints
    filtered_jobs = filter_jobs_by_constraints(
        jobs=all_jobs,
        required_skills=required_skills,
        preferred_locations=preferred_locations,
        remote_only=remote_only,
        visa_sponsorship_required=visa_sponsorship_required,
        min_salary=min_salary,
        experience_levels=experience_levels,
        job_types=job_types,
    )
    
    # Deduplicate
    unique_jobs = deduplicate_jobs(filtered_jobs)
    
    # Store new jobs
    new_count = store_jobs(unique_jobs)
    
    return {
        "success": True,
        "message": f"Found {len(unique_jobs)} matching jobs, {new_count} new jobs stored",
        "jobs": unique_jobs,
        "total_fetched": len(all_jobs),
        "total_matching": len(unique_jobs),
        "new_jobs_stored": new_count,
    }
