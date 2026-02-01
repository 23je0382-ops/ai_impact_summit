
import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
APPS_FILE = DATA_DIR / "applications.json"

def seed():
    DATA_DIR.mkdir(exist_ok=True)
    
    mock_apps = [
        {
            "id": str(uuid.uuid4()),
            "job_id": "job_1",
            "company_name": "Tech Corp",
            "job_title": "Software Engineer",
            "status": "submitted",
            "applied_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "notes": "Auto-submitted successfully"
        },
        {
            "id": str(uuid.uuid4()),
            "job_id": "job_2", 
            "company_name": "Startup Inc",
            "job_title": "AI Engineer",
            "status": "failed",
            "updated_at": datetime.utcnow().isoformat(),
            "notes": "Connection refused"
        },
        {
            "id": str(uuid.uuid4()),
            "job_id": "job_3",
            "company_name": "Big Bank",
            "job_title": "Data Analyst", 
            "status": "assembled",
            "updated_at": datetime.utcnow().isoformat(),
            "notes": "Ready for submission"
        }
    ]
    
    print(f"Seeding {len(mock_apps)} applications into {APPS_FILE}...")
    
    # Load existing to preserve any (unlikely if empty)
    existing_data = {"applications": []}
    if APPS_FILE.exists():
        try:
            with open(APPS_FILE, "r") as f:
                content = json.load(f)
                if isinstance(content, dict):
                    existing_data = content
                elif isinstance(content, list):
                    existing_data["applications"] = content
        except:
            pass
            
    # Merge
    existing_data["applications"].extend(mock_apps)
    
    with open(APPS_FILE, "w") as f:
        json.dump(existing_data, f, indent=2)
        
    print("Done.")

if __name__ == "__main__":
    seed()
