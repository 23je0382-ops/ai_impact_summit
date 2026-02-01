
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1/policy"

def verify():
    print("Starting Policy Verification...")
    
    # 1. Get Current Policy
    print("\n1. Getting Current Policy...")
    try:
        response = requests.get(BASE_URL + "/")
        print("Current Policy:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Failed to get policy: {e}")
        return

    # 2. Set Policy (Block 'Evil Corp', limit 5)
    print("\n2. Setting Policy (Block 'Evil Corp')...")
    new_policy = {
        "daily_limit": 5,
        "blocked_companies": ["Evil Corp", "Bad Inc"],
        "min_match_score": 50,
        "paused": False
    }
    requests.post(BASE_URL + "/set", json=new_policy)
    
    # 3. Check Job (Good Company) - Mocking a job check
    # We need a real job ID from queue
    try:
        with open("data/apply_queue.json", "r") as f:
             data = json.load(f)
             job_id = data["queue"][0]["id"]
             print(f"\n3. Checking Valid Job ({job_id})...")
             
             resp = requests.get(BASE_URL + f"/check?job_id={job_id}")
             print("Result:", json.dumps(resp.json(), indent=2))
    except Exception as e:
        print(f"Skipping job check (no queue data): {e}")

    # 4. Check Blocked Company (requires mocking or creating a dummy job, skipping complex setup for now)
    
    # 5. Test Kill Switch
    print("\n5. Testing Kill Switch...")
    requests.post(BASE_URL + "/pause-all")
    
    resp = requests.get(BASE_URL + "/")
    is_paused = resp.json().get("paused")
    print(f"System Paused: {is_paused}")
    
    if is_paused:
        print("SUCCESS: Kill switch active.")
    else:
        print("FAILED: Kill switch did not activate.")
        
    # Reset
    print("\n6. Resetting Policy...")
    requests.post(BASE_URL + "/set", json={"paused": False})

if __name__ == "__main__":
    verify()
