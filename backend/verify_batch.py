
import requests
import json
import time

BASE_URL = "http://localhost:8005/api/v1/apply/batch"

def verify():
    print("Starting Batch Verification on port 8005...")
    
    # 1. Start Batch
    print("\n1. Starting Batch Process...")
    try:
        resp = requests.post(f"{BASE_URL}/start", json={})
        print("Start Response:", json.dumps(resp.json(), indent=2))
    except Exception as e:
        print(f"Failed to start batch: {e}")
        return

    # 2. Poll Status (Monitor progress)
    print("\n2. Monitoring Status (Press Ctrl+C to stop early)...")
    for i in range(10): # Monitor for ~20 seconds
        try:
            resp = requests.get(f"{BASE_URL}/status")
            status = resp.json()
            
            print(f"[{i+1}/10] Status: {status.get('current_status')} | "
                  f"Processed: {status.get('processed_count')} | "
                  f"Success: {status.get('success_count')} | "
                  f"Failed: {status.get('failed_count')}")
            
            # Print latest log
            logs = status.get("logs", [])
            if logs:
                print(f"   Latest Log: {logs[-1]}")
            
            if status.get("current_status") == "completed":
                print("\nBatch Completed!")
                break
                
            time.sleep(2)
        except Exception as e:
            print(f"Error polling status: {e}")
            break

    # 3. Stop Batch
    print("\n3. Stopping Batch Process...")
    try:
        resp = requests.post(f"{BASE_URL}/stop")
        print("Stop Response:", json.dumps(resp.json(), indent=2))
        
        # Verify it stopped
        time.sleep(1)
        resp = requests.get(f"{BASE_URL}/status")
        print("Final Status:", resp.json().get("current_status"))
        
    except Exception as e:
        print(f"Failed to stop batch: {e}")

if __name__ == "__main__":
    verify()
