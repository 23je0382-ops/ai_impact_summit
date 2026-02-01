import requests
import json
from pathlib import Path

# Configuration
SANDBOX_URL = "http://localhost:8001/sandbox/jobs"
BACKEND_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
JOBS_FILE = BACKEND_DATA_DIR / "jobs.json"

def sync_jobs():
    print(f"Fetching jobs from Sandbox Portal: {SANDBOX_URL}")
    try:
        response = requests.get(SANDBOX_URL)
        if response.status_code != 200:
            print(f"Failed to fetch jobs: {response.status_code}")
            return
        
        sandbox_data = response.json()
        sandbox_jobs = sandbox_data.get("jobs", [])
        print(f"Found {len(sandbox_jobs)} jobs in Sandbox.")

        # Transform to backend format if necessary
        # The backend expects 'id', 'title', 'company', 'description', etc.
        # Sandbox has 'id', 'title', 'company', 'description', 'requirements', 'responsibilities'
        
        backend_jobs = []
        for s_job in sandbox_jobs:
            desc = s_job.get("description", "")
            reqs = "\n".join(s_job.get("requirements", []))
            resps = "\n".join(s_job.get("responsibilities", []))
            
            full_desc = f"{desc}\n\nRequirements:\n{reqs}\n\nResponsibilities:\n{resps}"
            
            b_job = {
                "id": s_job["id"],
                "title": s_job["title"],
                "company": s_job["company"],
                "location": s_job["location"],
                "description": full_desc,
                "url": f"http://localhost:8001/sandbox/jobs/{s_job['id']}",
                "posted_at": s_job.get("posted_date"),
                "is_remote": s_job.get("is_remote", False),
                "match_score": 85 # Default score for demo
            }
            backend_jobs.append(b_job)

        with open(JOBS_FILE, "r") as f:
            existing_data = json.load(f)
        
        # Merge or replace? Let's replace for the demo to ensure sync
        existing_data["jobs"] = backend_jobs
        existing_data["updated_at"] = sandbox_data.get("updated_at")

        with open(JOBS_FILE, "w") as f:
            json.dump(existing_data, f, indent=2)
        
        print(f"Successfully synced {len(backend_jobs)} jobs to {JOBS_FILE}")

    except Exception as e:
        print(f"Error syncing jobs: {e}")

if __name__ == "__main__":
    sync_jobs()
