
import requests
import json
import sys
from pathlib import Path

# Add parent directory to path to import app modules if needed (though we are testing via HTTP)
sys.path.append(str(Path(__file__).parent.parent))

def test_generate_answers():
    url = "http://localhost:8000/api/v1/student/generate-answers"
    
    # Mock profile based on the file we saw
    profile_data = {
            "education": [
                {
                    "degree": "Integrated Master of Technology in Mathematics and Computing",
                    "institution": "Indian Institute of Technology (ISM), Dhanbad",
                    "year": "Expected May 2028",
                    "gpa": "8.84/10.00"
                }
            ],
            "projects": [
                {
                    "name": "Machine Learning Algorithms from Scratch",
                    "description": "Implemented 10+ ML/DL algorithms...",
                    "technologies": ["Python", "NumPy"]
                }
            ],
            "experience": [],
            "skills": ["Python", "C++", "PyTorch"],
            "personal_info": {
                "name": "Vikas Gupta", 
                "email": "test@example.com"
            }
    }

    payload = {
        "profile_data": profile_data,
        "save_to_library": True
    }

    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Generated {len(data.get('answers', {}))} answers.")
            print(json.dumps(data, indent=2))
        else:
            print("Error Response:")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_generate_answers()
