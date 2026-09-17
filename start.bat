@echo off
cd /d "%~dp0"
echo ================================================================
echo   Iniciando APEX PRO - Plataforma de Telemetria de Alto Rendimiento
echo ================================================================

start "APEX Backend (FastAPI)" cmd /k "cd /d "%~dp0" && set PYTHONPATH=. && .\venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0"
timeout /t 3 >nul

start "APEX Frontend (Vite)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ================================================================
echo   Servidores iniciados correctamente:
echo    - Frontend Web: http://localhost:5180
echo    - Backend API:  http://localhost:8000/docs
echo ================================================================
echo.
pause
