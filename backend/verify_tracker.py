
import requests
import json
import time

BASE_URL = "http://localhost:8007/api/v1/tracker"

def verify():
    print("Starting Tracker Verification on port 8005...")
    
    # 1. Get Summary
    print("\n1. Testing Summary Endpoint...")
    try:
        resp = requests.get(f"{BASE_URL}/summary")
        summary = resp.json()
        print("Summary:", json.dumps(summary, indent=2))
        
        if "total_applications" not in summary:
            print("FAILED: Invalid summary structure")
            return
    except Exception as e:
        print(f"Summary failed: {e}")
        return

    # 2. List Applications (All)
    print("\n2. Testing List Endpoint (All)...")
    try:
        resp = requests.get(f"{BASE_URL}/applications?limit=2")
        apps = resp.json()
        print(f"Retrieved {len(apps)} applications.")
        if apps:
            print(f"Sample: {apps[0].get('job_id')} - {apps[0].get('status')}")
    except Exception as e:
        print(f"List failed: {e}")

    # 3. List Failures
    print("\n3. Testing Failures Endpoint...")
    try:
        resp = requests.get(f"{BASE_URL}/failures")
        failures = resp.json()
        print(f"Found {len(failures)} failures.")
        
        failed_app_id = None
        if failures:
            failed_app = failures[0]
            failed_app_id = failed_app.get("id")
            print("First Failure Details:", json.dumps(failed_app, indent=2))
    except Exception as e:
        print(f"Failures failed: {e}")

    # 4. Test Filters
    print("\n4. Testing Status Filter (status='failed')...")
    try:
        resp = requests.get(f"{BASE_URL}/applications?status=failed&limit=5")
        filtered = resp.json()
        print(f"Found {len(filtered)} items with status='failed'.")
    except Exception as e:
        print(f"Filter failed: {e}")
        
    # 5. Test Retry (Dry Run / Validation)
    if failed_app_id:
        print(f"\n5. Testing Retry for App ID: {failed_app_id}...")
        # Note: This might fail again if sandbox is down, but we check that the endpoint accepts it
        try:
            # We assume sandbox is still down, so it should attempt and maybe fail again, 
            # but getting a response (even error) confirms the endpoint works.
            resp = requests.post(f"{BASE_URL}/retry", json={"application_id": failed_app_id})
            print(f"Retry Response ({resp.status_code}):", resp.text[:200])
        except Exception as e:
            print(f"Retry request failed: {e}")
    else:
        print("\nSkipping Retry Test (No failed apps found).")

if __name__ == "__main__":
    verify()
