import asyncio
import httpx
import json
from app.services.auto_submit import submit_application
from app.services.data_store import load_applications

async def test_submission():
    # Find a job from the fresh queue
    with open("data/apply_queue.json", "r") as f:
        queue_data = json.load(f)
    
    queue = queue_data.get("queue", [])
    if not queue:
        print("No jobs found in data/apply_queue.json")
        return

    # Take the first job
    job = queue[0]
    job_id = job.get("id")
    
    print(f"Testing submission for {job.get('title')} at {job.get('company')} (Job ID: {job_id})")
    
    # We must assemble it first because auto_submit looks for an assembled package
    print("Assembling package...")
    from app.services.application_assembler import assemble_application_package
    assemble_application_package(job_id)

    try:
        # Note: submit_application reads from load_applications() inside itself
        # It finds the entry by job_id and uses its application_package
        result = await submit_application(job_id)
        print("Submission successful!")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Submission failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_submission())
