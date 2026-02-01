
"""
Seed Demo Data Script

Populates the application with realistic demo data for testing and demonstration.
- Student Profile (IIT Student Template)
- 50+ Job Listings
- Bullet Bank
- Answer Library
- Default Policies
"""

import sys
import uuid
import random
from datetime import datetime
from pathlib import Path

# Add backend directory to path so we can import app modules
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

from app.services.data_store import save_student_profile, save_jobs
from app.services.apply_policy import set_policy
from app.services.bullet_storage import save_bullets, clear_all_bullets
from app.services.answer_library import save_answers

def seed_profile():
    print("Seeding Student Profile...")
    profile = {
        "name": "Arjun Sharma",
        "contact_info": {
            "email": "arjun.sharma@iitb.ac.in",
            "phone": "+91 98765 43210",
            "location": "Mumbai, India",
            "linkedin": "linkedin.com/in/arjunsharma-cs",
            "github": "github.com/arjun-codes",
            "portfolio": "arjunsharma.dev"
        },
        "education": [
            {
                "degree": "B.Tech in Computer Science and Engineering",
                "school": "Indian Institute of Technology, Bombay",
                "year": "2025",
                "gpa": "9.2/10.0"
            }
        ],
        "experience": [
            {
                "company": "Swiggy",
                "role": "Software Engineering Intern",
                "location": "Bangalore",
                "duration": "May 2024 - July 2024",
                "description": "Optimized delivery route algorithm using graph neural networks."
            },
            {
                "company": "Krutrim SI Designs",
                "role": "AI Research Intern",
                "location": "Remote",
                "duration": "May 2023 - July 2023",
                "description": "Fine-tuned LLMs for indic language translation tasks."
            }
        ],
        "projects": [
            {
                "title": "ResumeAI",
                "tech_stack": ["Python", "FastAPI", "React", "OpenAI"],
                "description": "Automated resume tailoring system using LLMs."
            },
            {
                "title": "CryptoTrade Bot",
                "tech_stack": ["Node.js", "Redis", "WebSockets"],
                "description": "High-frequency trading bot with <50ms latency."
            },
            {
                "title": "Distributed File System",
                "tech_stack": ["Go", "gRPC", "Raft Consensus"],
                "description": "Fault-tolerant distributed storage system."
            }
        ],
        "skills": [
            "Python", "C++", "JavaScript", "Go",
            "React", "FastAPI", "Node.js", "Django",
            "PyTorch", "TensorFlow", "scikit-learn",
            "AWS", "Docker", "Kubernetes", "Git"
        ]
    }
    save_student_profile(profile)

def seed_jobs():
    print("Seeding 50+ Job Listings...")
    roles = [
        "Software Engineer", "Backend Developer", "Frontend Developer", 
        "Full Stack Engineer", "Machine Learning Engineer", "Data Scientist", 
        "DevOps Engineer", "Cloud Architect", "Product Manager", "AI Research Scientist"
    ]
    companies = [
        "Google", "Microsoft", "Amazon", "Uber", "Airbnb", 
        "Flipkart", "Razorpay", "Cred", "Zerodha", "Postman",
        "Zomato", "Swiggy", "Ola Electric", "PhonePe", "Groww",
        "Atlassian", "Salesforce", "Oracle", "Adobe", "Intuit",
        "Goldman Sachs", "JPMorgan Chase", "Morgan Stanley", "Tower Research", "D. E. Shaw"
    ]
    locations = ["Bangalore", "Mumbai", "Gurgaon", "Hyderabad", "Pune", "Remote", "Noida", "Chennai"]
    
    jobs = []
    
    # Generate 55 jobs
    for i in range(55):
        role = random.choice(roles)
        company = random.choice(companies)
        location = random.choice(locations)
        is_remote = location == "Remote"
        
        # Simple varied descriptions
        desc_templates = [
            f"We are looking for a talented {role} to join our team at {company}. You will work on scalable systems.",
            f"{company} is hiring a {role} to build next-gen products. Experience in Python and AWS required.",
            f"Join {company} as a {role}. We are revolutionizing the industry. Strong CS fundamentals needed.",
            f"Exciting opportunity for a {role} at {company}. Work on high-impact projects in {location}."
        ]
        
        job = {
            "id": str(uuid.uuid4()),
            "title": f"{role} {'(New Grad)' if i % 5 == 0 else ''}",
            "company": company,
            "location": location,
            "description": random.choice(desc_templates) + "\n\nRequirements:\n- Bachelor's degree in CS\n- Experience with Java/Python\n- Strong problem solving skills",
            "url": f"https://careers.{company.lower().replace(' ', '')}.com/jobs/{random.randint(10000, 99999)}",
            "posted_at": datetime.utcnow().isoformat(),
            "is_remote": is_remote,
            "match_score": random.randint(60, 98) # Random score to test ranking/policy
        }
        jobs.append(job)
        
    save_jobs(jobs)

def seed_bullets():
    print("Seeding Bullet Bank...")
    clear_all_bullets()
    
    bullets = [
        # Swiggy
        {
            "id": str(uuid.uuid4()),
            "content": "Optimized delivery route planning algorithm using Graph Neural Networks, reducing average delivery time by 15%.",
            "source_name": "Swiggy Internship",
            "source_type": "experience",
            "categories": ["Machine Learning", "Optimization", "Python"],
            "has_metrics": True,
            "is_grounded": True
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Collaborated with backend team to integrate real-time traffic data into the routing engine handling 1M+ requests/day.",
            "source_name": "Swiggy Internship",
            "source_type": "experience",
            "categories": ["Backend", "Scalability", "Collaboration"],
            "has_metrics": True,
            "is_grounded": True
        },
        # Krutrim
        {
            "id": str(uuid.uuid4()),
            "content": "Fine-tuned Llama-2-7b on a curated dataset of 50k local language pairs, improving Hindi-English translation BLEU score by 4.5 points.",
            "source_name": "Krutrim Internship",
            "source_type": "experience",
            "categories": ["AI/ML", "LLMs", "NLP"],
            "has_metrics": True,
            "is_grounded": True
        },
        # ResumeAI Project
        {
            "id": str(uuid.uuid4()),
            "content": "Architected an autonomous agent system using LangChain and FastAPI to generate tailored resumes, serving 500+ users.",
            "source_name": "ResumeAI Project",
            "source_type": "project",
            "categories": ["Full Stack", "AI Engineering", "Product"],
            "has_metrics": True,
            "is_grounded": True
        },
        # CryptoBot
        {
            "id": str(uuid.uuid4()),
            "content": "Engineered a low-latency trading engine in Node.js processing market data updates in under 50ms using WebSockets.",
            "source_name": "CryptoTrade Bot",
            "source_type": "project",
            "categories": ["Low Latency", "Systems", "JavaScript"],
            "has_metrics": True,
            "is_grounded": True
        }
    ]
    
    save_bullets(bullets, profile_id="demo_user")

def seed_answers():
    print("Seeding Answer Library...")
    
    # We populate the dictionary structure expected by save_answers
    # format: category_name -> single answer object (which contains 'answer' text)
    
    answers = {}
    
    # Why Company
    answers["why_company"] = {
        "id": str(uuid.uuid4()),
        "category": "why_company",
        "answer": "I have always admired [COMPANY_NAME]'s commitment to innovation and engineering excellence. As someone passionate about building scalable distributed systems, I am excited by the technical challenges your team tackles. I believe my background in high-performance computing and my experience at Swiggy make me a strong fit for the [ROLE] position.",
        "needs_editing": True,
        "is_template": True
    }
    
    # Strengths
    answers["strengths"] = {
        "id": str(uuid.uuid4()),
        "category": "strengths",
        "answer": "My greatest strength is my ability to solve complex algorithmic problems efficiently. At IIT Bombay, I maintained a 9.2 GPA while leading technical projects like a distributed file system. I thrive in fast-paced environments where I can apply my deep understanding of data structures and ML models to drive tangible performance improvements.",
        "needs_editing": False,
        "is_template": False
    }
    
    # Career Goals
    answers["career_goals"] = {
        "id": str(uuid.uuid4()),
        "category": "career_goals",
        "answer": "My goal is to grow as a technical architect in a leading product company. Over the next few years, I want to deepen my expertise in large-scale AI systems and eventually lead engineering teams building impactful products. I see this role as the perfect foundation to apply my research skills in a production setting.",
        "needs_editing": False,
        "is_template": False
    }
    
    save_answers(answers)

def seed_policy():
    print("Seeding Policies...")
    set_policy({
        "daily_limit": 25,
        "min_match_score": 70,
        "blocked_companies": ["Revature", "Infosys", "TCS"], # Just examples
        "paused": False,
        "remote_only_enforced": False
    })

def main():
    print("--- Starting Demo Data Seeding ---")
    try:
        seed_profile()
        seed_jobs()
        seed_bullets()
        seed_answers()
        seed_policy()
        print("\n--- ✅ Demo Data Seeded Successfully ---")
    except Exception as e:
        print(f"\n--- ❌ Seeding Failed: {e} ---")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
