
import asyncio
import httpx

async def test_rank():
    payload = {
        "profile_data": {"skills": ["Python", "C++"], "experience": []},
        "limit": 10,
        "auto_queue": False
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post("http://localhost:8000/api/jobs/rank", json=payload)
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_rank())
