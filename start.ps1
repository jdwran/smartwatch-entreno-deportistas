$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Iniciando APEX PRO - Plataforma de Telemetria Fisiologica     " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Start Backend
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='.'; Set-Location '$ScriptDir'; .\venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0"

Start-Sleep -Seconds 2

# Start Frontend
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "Set-Location '$ScriptDir\frontend'; npm run dev"

Write-Host ""
Write-Host "Servidores iniciados en ventanas dedicadas:" -ForegroundColor Green
Write-Host " - Frontend Web: http://localhost:5180" -ForegroundColor Yellow
Write-Host " - Backend Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
