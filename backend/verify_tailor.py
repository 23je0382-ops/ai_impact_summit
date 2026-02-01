
import asyncio
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.resume_tailor import tailor_resume
from app.services.cover_letter import generate_cover_letter
from app.services.evidence_mapper import map_evidence
from app.services.data_store import save_student_profile

def verify():
    print("Starting verification (Evidence & Transparency)...")
    
    # UUID from apply_queue.json
    job_id = "2596910b-095d-49d9-bf18-4048c100cd14"
    
    # Mock profile
    profile = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "education": [{"degree": "BS CS", "school": "Tech Univ", "year": "2024"}],
        "skills": ["Python", "FastAPI", "React", "AWS", "Java", "Docker"],
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Intern",
                "responsibilities": ["Built python APIs", "Used AWS services"]
            }
        ]
    }
    
    try:
        print("\n--- Testing Evidence Mapper ---")
        mapping = map_evidence(job_id, profile)
        print("Evidence Mapping Generated:")
        print(json.dumps(mapping, indent=2))
        
        # Validate structure
        assert isinstance(mapping, list)
        if len(mapping) > 0:
            assert "requirement" in mapping[0]
            assert "evidence_type" in mapping[0]
        
        print("\nSUCCESS: Mapping structure valid.")
        
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
