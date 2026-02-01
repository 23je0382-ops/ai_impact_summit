"""
Clean Queue Script

Removes invalid/placeholder jobs from the apply queue that don't exist in the Sandbox Portal.
"""

import json
import requests
from pathlib import Path
from datetime import datetime

SANDBOX_URL = "http://localhost:8001/sandbox/jobs"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
QUEUE_FILE = DATA_DIR / "apply_queue.json"

def clean_queue():
    print("Fetching valid jobs from Sandbox Portal...")
    try:
        response = requests.get(SANDBOX_URL)
        if response.status_code != 200:
            print(f"Failed to fetch jobs from Sandbox: {response.status_code}")
            return
        
        sandbox_data = response.json()
        valid_job_ids = {job["id"] for job in sandbox_data.get("jobs", [])}
        print(f"Found {len(valid_job_ids)} valid jobs in Sandbox Portal.")
        
    except Exception as e:
        print(f"Error fetching from Sandbox: {e}")
        return

    # Load current queue
    with open(QUEUE_FILE, "r") as f:
        queue_data = json.load(f)
    
    original_queue = queue_data.get("queue", [])
    original_count = len(original_queue)
    
    # Filter to only valid jobs
    cleaned_queue = [job for job in original_queue if job.get("id") in valid_job_ids]
    removed_count = original_count - len(cleaned_queue)
    
    print(f"Removed {removed_count} invalid jobs from queue.")
    print(f"Remaining jobs in queue: {len(cleaned_queue)}")
    
    # Save cleaned queue
    queue_data["queue"] = cleaned_queue
    queue_data["updated_at"] = datetime.now().isoformat()
    
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue_data, f, indent=2)
    
    print("Queue cleaned and saved.")

if __name__ == "__main__":
    clean_queue()
