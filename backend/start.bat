@echo off
REM Start the inf-canvas backend (FastAPI + Uvicorn).
REM Usage:  start.bat            -> runs on port 8000
REM         start.bat 9000       -> runs on a custom port

cd /d "%~dp0"

set "PORT=%~1"
if "%PORT%"=="" set "PORT=8000"

where uv >nul 2>nul
if errorlevel 1 (
  echo [error] 'uv' was not found on PATH.
  echo Restart VS Code/your terminal, or install uv: pip install uv
  exit /b 1
)

echo Starting backend on http://localhost:%PORT%  (Ctrl+C to stop)
uv run uvicorn inf_canvas.main:app --reload --port %PORT%
