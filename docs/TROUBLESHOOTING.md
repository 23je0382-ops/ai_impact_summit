
# Troubleshooting Guide

Common issues and solutions for the AI Job Impact Agent.

## 1. Application Errors (Frontend)

### "Something went wrong" White Screen
**Cause**: An unhandled error crashed the React component tree.
**Solution**:
1.  Click the **Reload Page** button in the error view.
2.  Check the browser console (F12) for specific stack traces.
3.  Ensure the API server is running on port 8000.

### "Failed to load..." / Network Errors
**Cause**: Backend API is unreachable or timing out.
**Solution**:
1.  Verify Backend is running: `http://localhost:8000/api/health` should return `{"status": "healthy"}`.
2.  Check CORS settings in `.env` if accessing from a different device.
3.  Check `VITE_API_URL` in `frontend/.env` matches your backend address.

## 2. Backend & System Errors

### "Batch already running"
**Cause**: You tried to start the batch processor while it was active.
**Solution**:
1.  Wait for the current batch to finish.
2.  Or stop it manually via the API/Dashboard.
3.  If "stuck" (process crashed but state is locked), restart the backend server: `Ctrl+C` then `uvicorn app.main:app --reload`.

### 422 Unprocessable Entity
**Cause**: Invalid data sent to the API.
**Solution**:
1.  Check the API response body in the browser Network tab. It lists the exact field failing validation.
2.  Likely culprits: Missing `job_id`, invalid email format, or negative salary numbers.

### 500 Internal Server Error
**Cause**: Unexpected crash in the backend logic.
**Solution**:
1.  Check the terminal where `uvicorn` is running. The specific python traceback will be printed there.
2.  Look for `Unhandled exception:` in the logs.

## 3. Demo Script Issues

### "Simulated Gateway Timeout"
**Cause**: The demo script (`run_demo.py`) randomly simulates failures (10% chance) to demonstrate error handling.
**Solution**: This is expected behavior! It proves the system tracks failures correctly. Rerun the script for a different outcome.

### "Connection Refused" (Sandbox)
**Cause**: The `auto_submit` service can't reach the submission portal.
**Solution**:
- For the Demo Script: It uses a mock submitter, so this shouldn't happen.
- For Real Usage: Ensure the target portal is online.

## 4. Resetting the System

If the database is corrupted or you want a fresh start:
1.  **Stop Servers**: Kill all terminal processes.
2.  **Clear Data**: Delete `backend/data/*.json`.
3.  **Seed Data**: Run `python backend/scripts/seed_demo_data.py`.
4.  **Restart**: Run `uvicorn ...` and `npm run dev`.
