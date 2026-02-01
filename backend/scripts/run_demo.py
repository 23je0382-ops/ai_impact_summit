
"""
Run Demo Script

Executes an automated end-to-end demo of the job application agent.
"""

import sys
import asyncio
import time
import json
import random
from pathlib import Path
from datetime import datetime

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

# Import Services
from app.services.data_store import load_jobs, load_student_profile, save_jobs, update_application, load_applications
from app.services.job_ranker import rank_jobs, add_to_apply_queue
from app.services.application_assembler import assemble_application_package
from scripts.seed_demo_data import seed_profile, seed_jobs, seed_bullets, seed_answers

def print_step(msg):
    print(f"\n[DEMO] {msg}")
    print("-" * 50)

async def mock_submit_application(job_id: str):
    """
    Simulate submission for reliable demo execution.
    Updates the local application state to 'submitted' without hitting external API.
    """
    # 1. Find App
    apps = load_applications()
    candidates = [a for a in apps if a.get("job_id") == job_id and a.get("status") == "assembled"]
    if not candidates:
        return {"status": "failed", "error": "No assembled app found"}
    
    app_id = candidates[0]['id']
    
    # 2. Simulate Network Delay
    delay = random.uniform(0.5, 1.5)
    await asyncio.sleep(delay)
    
    # 3. Success (90% chance) or Failure
    if random.random() > 0.1:
        receipt = {"id": f"sub_{random.randint(10000,99999)}", "time": datetime.utcnow().isoformat()}
        update_application(app_id, {
            "status": "submitted",
            "submitted_at": datetime.utcnow().isoformat(),
            "submission_receipt": receipt,
            "notes": "Auto-submitted via Demo Script"
        })
        return {"status": "success", "receipt": receipt}
    else:
        update_application(app_id, {
            "status": "failed",
            "notes": "Simulated submission failure"
        })
        return {"status": "failed", "error": "Simulated Gateway Timeout"}

async def main():
    print("==================================================")
    print("      AI AGENT: AUTONOMOUS APPLICATION DEMO       ")
    print("==================================================")
    
    start_time = time.time()
    
    # 1. Import Student Resume & Profile
    print_step("Step 1: Importing Student Persona & History")
    seed_profile()
    seed_bullets()
    seed_answers()
    
    profile = load_student_profile()
    print(f"Loaded Profile: {profile['name']}")
    print(f"Education: {profile['education'][0]['degree']} from {profile['education'][0]['school']}")
    print(f"Experience: {len(profile['experience'])} roles")
    print(f"Artifacts: {len(load_jobs())} jobs (clearing...), 5 verified bullets")

    # 2. Search & Rank Jobs
    print_step("Step 2: AI Job Search & Ranking")
    seed_jobs() # Simulating "Search" returning results
    all_jobs = load_jobs()
    print(f"\nFound {len(all_jobs)} potential job matches.")
    
    print("Ranking jobs based on profile match...")
    
    # Ensure rankings are fresh and logic runs
    ranked_jobs = rank_jobs(all_jobs, profile)
    
    print("\nTop 5 Ranked Jobs:")
    for i, job in enumerate(ranked_jobs[:5], 1):
        print(f"{i}. {job['title']} at {job['company']} (Score: {job['match_score']})")
        if "match_reasoning" in job:
            print(f"   Reason: {job['match_reasoning']}")

    # 3. Queue Management
    print_step("Step 3: Populating Application Queue")
    top_15 = ranked_jobs[:15]
    count = add_to_apply_queue(top_15)
    print(f"Added {count} high-priority jobs to the Apply Queue.")

    # 4. Auto-Application Loop
    print_step("Step 4: Autonomous Application Execution (Processing Top 10)")
    
    results = []
    
    # Process top 10
    jobs_to_apply = top_15[:10]
    
    print(f"{'COMPANY':<20} {'ROLE':<30} {'STATUS':<15} {'TIME'}")
    print("-" * 75)
    
    for job in jobs_to_apply:
        job_start = time.time()
        status = "Failed"
        details = ""
        
        try:
            # Assemble (REAL)
            pkg = assemble_application_package(job["id"])
            
            # Submit (MOCKED for Demo Reliability)
            res = await mock_submit_application(job["id"])
            
            if res["status"] == "success":
                status = "Submitted"
            else:
                status = "Failed"
                details = res.get("error", "Unknown")
                
        except Exception as e:
            status = "Error"
            details = str(e)
            
        duration = time.time() - job_start
        print(f"{job['company']:<20} {job['title'][:28]:<30} {status:<15} {duration:.1f}s")
        
        results.append({
            "company": job["company"],
            "status": status,
            "duration": duration,
            "details": details
        })
        
    # 5. Summary Report
    print_step("Step 5: Final Execution Report")
    
    total_time = time.time() - start_time
    success_count = sum(1 for r in results if r["status"] == "Submitted")
    
    print(f"Total Execution Time: {total_time:.2f}s")
    print(f"Applications Attempted: {len(results)}")
    print(f"Successfully Submitted: {success_count}")
    print(f"Success Rate: {(success_count/len(results))*100:.1f}%")
    
    print("\nDetailed Breakdown:")
    for r in results:
        if r["status"] != "Submitted":
             print(f"- Failed: {r['company']} ({r['details']})")

    print("\n[DEMO] Completed Successfully.")

if __name__ == "__main__":
    asyncio.run(main())
