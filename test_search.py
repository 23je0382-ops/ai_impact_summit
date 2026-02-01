
import asyncio
import httpx

async def test_search():
    payload = {
        "required_skills": ["Python"],
        "min_salary": 100000
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post("http://localhost:8000/api/jobs/search", json=payload)
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
