
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1/apply/assemble"

def verify():
    print("Starting Application Assembly Verification...")
    
    # 1. Get a Job ID from Queue
    try:
        with open("data/apply_queue.json", "r") as f:
             data = json.load(f)
             if not data.get("queue"):
                 print("No jobs in queue to test with.")
                 return
             job_id = data["queue"][0]["id"]
             print(f"Using Job ID: {job_id}")
    except Exception as e:
        print(f"Failed to read queue: {e}")
        return

    # 2. Mock Profile Data (Optional, passing it explicitly to be safe)
    payload = {
        "job_id": job_id,
        "profile_data": {
            "name": "Test Student",
            "email": "test@student.com",
            "skills": ["Python", "FastAPI", "React", "AWS"],
            "experience": [
                {
                    "company": "Tech Corp",
                    "role": "Intern",
                    "responsibilities": ["Built python APIs", "Deployed strictly to AWS"]
                }
            ]
        }
    }

    # 3. Call Assemble Endpoint
    print("\nCalling text assembly endpoint...")
    start = time.time()
    try:
        response = requests.post(BASE_URL, json=payload)
        duration = time.time() - start
        
        if response.status_code == 200:
            pkg = response.json()
            print(f"SUCCESS! Assembly took {duration:.2f}s")
            print(f"Package ID: {pkg.get('id')}")
            print(f"Created Application ID: {pkg.get('application_id')}")
            
            # Check components
            artifacts = pkg.get("artifacts", {})
            print(f"- Resume Present: {bool(artifacts.get('resume'))}")
            print(f"- Cover Letter Length: {len(artifacts.get('cover_letter', ''))} chars")
            print(f"- Evidence Items: {len(artifacts.get('evidence_map', []))}")
            print(f"- Answers Generated: {len(artifacts.get('questionnaire_answers', {}))}")
            
        else:
            print(f"FAILED: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    verify()
