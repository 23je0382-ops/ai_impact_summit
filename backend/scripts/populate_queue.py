import json
from pathlib import Path
from datetime import datetime

BACKEND_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
JOBS_FILE = BACKEND_DATA_DIR / "jobs.json"
QUEUE_FILE = BACKEND_DATA_DIR / "apply_queue.json"

def populate_queue():
    with open(JOBS_FILE, "r") as f:
        jobs_data = json.load(f)
    
    jobs = jobs_data.get("jobs", [])
    if not jobs:
        print("No jobs found in jobs.json")
        return

    queue_items = []
    for job in jobs[:10]: # Add top 10
        queue_items.append({
            "id": job["id"],
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "description": job["description"],
            "url": job["url"],
            "posted_at": job["posted_at"],
            "is_remote": job["is_remote"],
            "match_score": job["match_score"],
            "status": "queued",
            "queued_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    queue_data = {
        "queue": queue_items,
        "updated_at": datetime.now().isoformat()
    }

    with open(QUEUE_FILE, "w") as f:
        json.dump(queue_data, f, indent=2)
    
    print(f"Successfully populated queue with {len(queue_items)} valid jobs from Sandbox.")

if __name__ == "__main__":
    populate_queue()
