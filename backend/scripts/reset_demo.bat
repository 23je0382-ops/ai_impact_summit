@echo off
echo ===========================================
echo      RESETTING AI AGENT DEMO ENVIRONMENT
echo ===========================================

cd /d "%~dp0"
echo Switch to backend directory...

:: Check if venv exists
if exist "..\venv\Scripts\python.exe" (
    echo Using Virtual Environment...
    "..\venv\Scripts\python.exe" seed_demo_data.py
) else (
    echo Venv not found, trying global python...
    python seed_demo_data.py
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Database reset and seeded with Arjun Sharma profile.
    echo Ready for recording!
) else (
    echo.
    echo [ERROR] Seeding failed. Check logs.
)

pause
