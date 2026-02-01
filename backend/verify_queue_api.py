
import requests
import json
import time

BASE_URL = "http://localhost:8008/api/v1/apply/queue"

def verify():
    print("Starting Queue API Verification on port 8007...")
    
    # 1. Get Queue (Empty initially?)
    print("\n1. Get Queue...")
    try:
        resp = requests.get(BASE_URL)
        print("Queue:", json.dumps(resp.json(), indent=2))
        
        queue = resp.json().get("queue", [])
        if not isinstance(queue, list):
            print("FAILED: Queue is not a list")
            return
            
    except Exception as e:
        print(f"Get Queue failed: {e}")
        return

    # 2. Add item to queue (Need to simulate this? Using job ranker or manual file edit?)
    # Since we don't have a direct "add to queue" API (it's internal via Rank), 
    # we can try to re-use an existing job ID from seeded data if we can "queue" it.
    # Or just verify empty queue behavior is correct.
    # To truly test remove/reorder, we need items.
    
    # Let's manually seed the queue file for this test since we can't easily invoke "Rank" from here without profile data.
    from pathlib import Path
    DATA_DIR = Path("data")
    QUEUE_FILE = DATA_DIR / "apply_queue.json"
    
    mock_queue = [
        {"id": "job_a", "title": "Job A", "match_score": 90},
        {"id": "job_b", "title": "Job B", "match_score": 80},
        {"id": "job_c", "title": "Job C", "match_score": 70}
    ]
    
    import threading
    # Just write directly, ignore lock for test script
    with open(QUEUE_FILE, "w") as f:
        json.dump({"queue": mock_queue}, f)
        
    print("\nSeeded 3 jobs to queue file.")
    
    # 3. Get Queue Again
    print("\n3. Get Queue (Seeded)...")
    try:
        resp = requests.get(BASE_URL)
        queue = resp.json().get("queue", [])
        print(f"Queue Length: {len(queue)}")
        if len(queue) != 3:
            print("FAILED: Queue length mismatch")
    except Exception as e:
        print(f"Get Queue failed: {e}")

    # 4. Remove Item
    print("\n4. Remove Job B...")
    try:
        resp = requests.delete(f"{BASE_URL}/job_b")
        print("Remove Response:", resp.json())
        
        resp = requests.get(BASE_URL)
        queue = resp.json().get("queue", [])
        ids = [j["id"] for j in queue]
        print("Current IDs:", ids)
        if "job_b" in ids:
            print("FAILED: Job B still in queue")
    except Exception as e:
        print(f"Remove failed: {e}")

    # 5. Reorder (Swap A and C)
    print("\n5. Reorder (C first)...")
    try:
        new_order = ["job_c", "job_a"]
        resp = requests.post(f"{BASE_URL}/reorder", json={"job_ids": new_order})
        print("Reorder Response:", resp.json())
        
        resp = requests.get(BASE_URL)
        queue = resp.json().get("queue", [])
        ids = [j["id"] for j in queue]
        print("Current IDs:", ids)
        if ids != new_order:
             print("FAILED: Order mismatch")
    except Exception as e:
        print(f"Reorder failed: {e}")

if __name__ == "__main__":
    verify()
