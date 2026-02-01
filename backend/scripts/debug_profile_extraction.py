
import requests
import sys
import os

def create_dummy_pdf(filename="test_resume.pdf"):
    try:
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(filename)
        c.drawString(100, 750, "Vikas Gupta")
        c.drawString(100, 730, "Email: test@example.com")
        c.drawString(100, 710, "Experience: Software Engineer at Tech Corp (2020-2022)")
        c.save()
        print(f"Created {filename}")
        return filename
    except ImportError:
        print("ReportLab not installed, skipping PDF creation. Please ensure a PDF exists.")
        return None

def test_extract_profile():
    base_url = "http://localhost:8000/api/v1/student"
    
    # 1. Upload Resume
    pdf_path = "test_resume.pdf"
    if not os.path.exists(pdf_path):
        created = create_dummy_pdf(pdf_path)
        if not created:
            return

    print(f"Uploading {pdf_path}...")
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path, f, 'application/pdf')}
            response = requests.post(f"{base_url}/upload-resume", files=files)
            
        if response.status_code != 200:
            print(f"Upload failed: {response.text}")
            return
            
        upload_data = response.json()
        resume_id = upload_data['id']
        print(f"Resume uploaded. ID: {resume_id}")
        
        # 2. Extract Profile
        print(f"Extracting profile for ID: {resume_id}...")
        payload = {"resume_id": resume_id}
        response = requests.post(f"{base_url}/extract-profile", json=payload)
        
        if response.status_code == 200:
            print("Profile Extraction Success!")
            print(response.json())
        else:
            print(f"Profile Extraction Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_extract_profile()
