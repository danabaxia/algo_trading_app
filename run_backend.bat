@echo off
echo Starting Backend API...
call venv\Scripts\activate
uvicorn api.main:app --reload --port 8001
pause
