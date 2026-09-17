from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from backend.app.models.schemas import (
    AthleteProfile,
    WorkoutSession,
    HRVReading,
    SleepRecord,
    WorkloadDay,
    DailyReadiness,
    ProviderConnection
)
from backend.app.ingestion.mock_generator import mock_db
from backend.app.ingestion.fit_parser import parse_fit_file_bytes
from backend.app.sports_science.hrv_engine import analyze_hrv_readiness

router = APIRouter(prefix="/api")


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "Sports Science Telemetry Engine v1.0"}


@router.get("/athletes", response_model=List[AthleteProfile])
def list_athletes():
    return list(mock_db.athletes.values())


@router.get("/athletes/{athlete_id}", response_model=AthleteProfile)
def get_athlete(athlete_id: str):
    if athlete_id not in mock_db.athletes:
        raise HTTPException(status_code=404, detail="Atleta no encontrado")
    return mock_db.athletes[athlete_id]


@router.get("/athletes/{athlete_id}/readiness", response_model=Dict[str, Any])
def get_athlete_readiness(athlete_id: str):
    if athlete_id not in mock_db.athletes:
        raise HTTPException(status_code=404, detail="Atleta no encontrado")
        
    readiness_list = mock_db.daily_readiness.get(athlete_id, [])
    if not readiness_list:
        raise HTTPException(status_code=404, detail="No hay datos de preparación")
        
    current = readiness_list[-1]
    history = readiness_list[-14:]  # Last 14 days
    
    # Recent HRV baseline data
    hrv_readings = mock_db.hrv_records.get(athlete_id, [])[-14:]
    
    return {
        "current": current,
        "history": history,
        "hrv_readings": hrv_readings
    }


@router.get("/athletes/{athlete_id}/workouts", response_model=List[WorkoutSession])
def get_athlete_workouts(athlete_id: str, limit: int = 15):
    if athlete_id not in mock_db.athletes:
        raise HTTPException(status_code=404, detail="Atleta no encontrado")
    workouts = mock_db.workouts.get(athlete_id, [])
    # Return sorted descending by start_time
    return sorted(workouts, key=lambda w: w.start_time, reverse=True)[:limit]


@router.get("/athletes/{athlete_id}/sleep", response_model=Dict[str, Any])
def get_athlete_sleep(athlete_id: str, limit: int = 14):
    if athlete_id not in mock_db.athletes:
        raise HTTPException(status_code=404, detail="Atleta no encontrado")
    records = mock_db.sleep_records.get(athlete_id, [])[-limit:]
    current = records[-1] if records else None
    
    # Calculate sleep averages
    if records:
        avg_efficiency = round(sum(r.efficiency_percentage for r in records) / len(records), 1)
        avg_deep = round(sum(r.deep_sleep_minutes for r in records) / len(records), 0)
        avg_rem = round(sum(r.rem_sleep_minutes for r in records) / len(records), 0)
        avg_score = round(sum(r.sleep_score for r in records) / len(records), 0)
    else:
        avg_efficiency = 0
        avg_deep = 0
        avg_rem = 0
        avg_score = 0
        
    return {
        "current": current,
        "history": records,
        "averages": {
            "efficiency": avg_efficiency,
            "deep_minutes": avg_deep,
            "rem_minutes": avg_rem,
            "score": avg_score
        }
    }


@router.get("/athletes/{athlete_id}/workload", response_model=Dict[str, Any])
def get_athlete_workload(athlete_id: str):
    if athlete_id not in mock_db.athletes:
        raise HTTPException(status_code=404, detail="Atleta no encontrado")
    history = mock_db.workload_history.get(athlete_id, [])
    current = history[-1] if history else None
    return {
        "current": current,
        "history": history
    }


@router.get("/athletes/{athlete_id}/integrations", response_model=List[ProviderConnection])
def get_athlete_integrations(athlete_id: str):
    if athlete_id not in mock_db.athletes:
        raise HTTPException(status_code=404, detail="Atleta no encontrado")
    return mock_db.connections.get(athlete_id, [])


@router.post("/athletes/{athlete_id}/integrations/{provider_id}/toggle")
def toggle_integration(athlete_id: str, provider_id: str):
    from datetime import datetime, timezone
    if athlete_id not in mock_db.athletes:
        raise HTTPException(status_code=404, detail="Atleta no encontrado")
        
    conns = mock_db.connections.get(athlete_id, [])
    found = False
    for conn in conns:
        if conn.provider_id == provider_id:
            conn.connected = not conn.connected
            conn.last_sync = datetime.now(timezone.utc) if conn.connected else None
            found = True
            return {"status": "success", "provider": conn}
            
    if not found:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")


@router.post("/upload/fit", response_model=Dict[str, Any])
async def upload_fit_file(
    file: UploadFile = File(...),
    athlete_id: str = Form(...)
):
    if athlete_id not in mock_db.athletes:
        raise HTTPException(status_code=404, detail="Atleta no encontrado")
        
    athlete = mock_db.athletes[athlete_id]
    content = await file.read()
    
    # Process through FIT parser
    workout = parse_fit_file_bytes(content, athlete, filename=file.filename or "workout.fit")
    
    # Append to athlete workouts
    mock_db.workouts[athlete_id].insert(0, workout)
    
    return {
        "status": "success",
        "message": f"Archivo '{file.filename}' procesado exitosamente.",
        "workout": workout
    }
