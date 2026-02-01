
import requests
import json
import time

BASE_URL = "http://localhost:8005/api/v1/apply"

def verify():
    print("Starting Application Submission Verification...")
    
    # 1. Get a Job ID from Queue
    try:
        with open("data/apply_queue.json", "r") as f:
             data = json.load(f)
             if not data.get("queue"):
                 print("No jobs in queue.")
                 return
             job_id = data["queue"][0]["id"]
             print(f"Using Job ID: {job_id}")
    except Exception as e:
        print(f"Failed to read queue: {e}")
        return

    # 2. Ensure Assembly Exists (Call Assemble First)
    print("\nEnsuring application is assembled...")
    payload_assemble = {"job_id": job_id}
    try:
        resp = requests.post(f"{BASE_URL}/assemble", json=payload_assemble)
        if resp.status_code == 200:
            print("Assembly confirmed.")
        else:
            print(f"Assembly failed: {resp.text}")
            return
    except Exception as e:
        print(f"Assembly request error: {e}")
        return

    # 3. Call Submit Endpoint
    print("\nCalling submit endpoint (Attempting to reach Sandbox at localhost:8001)...")
    payload_submit = {"job_id": job_id}
    
    start = time.time()
    try:
        response = requests.post(f"{BASE_URL}/submit", json=payload_submit)
        duration = time.time() - start
        
        print(f"Request took {duration:.2f}s")
        
        if response.status_code == 200:
            print("SUCCESS: Application Submitted!")
            print("Receipt:", json.dumps(response.json(), indent=2))
        else:
            print(f"Submission Failed (Expected if Sandbox not running): {response.status_code}")
            try:
                print("Error Details:", json.dumps(response.json(), indent=2))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    verify()
