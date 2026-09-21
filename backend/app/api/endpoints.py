from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from backend.app.models.schemas import (
    AthleteProfile,
    WorkoutSession,
    HRVReading,
    SleepRecord,
    WorkloadDay,
    DailyReadiness,
    ProviderConnection,
    OrthostaticTestRecord,
    FatigueAnalysis
)
from backend.app.ingestion.mock_generator import mock_db
from backend.app.ingestion.fit_parser import parse_fit_file_bytes
from backend.app.sports_science.hrv_engine import analyze_hrv_readiness
from backend.app.sports_science.fatigue_engine import evaluate_orthostatic_test, synthesize_athlete_fatigue

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


@router.get("/athletes/{athlete_id}/fatigue", response_model=Dict[str, Any])
def get_athlete_fatigue(athlete_id: str):
    if athlete_id not in mock_db.athletes:
        raise HTTPException(status_code=404, detail="Atleta no encontrado")
        
    fatigue_list = mock_db.fatigue_history.get(athlete_id, [])
    if not fatigue_list:
        raise HTTPException(status_code=404, detail="No hay datos de fatiga")
        
    current = fatigue_list[-1]
    history = fatigue_list[-14:]
    ortho_latest = mock_db.orthostatic_tests.get(athlete_id, [])[-1] if mock_db.orthostatic_tests.get(athlete_id) else None
    
    return {
        "current": current,
        "history": history,
        "latest_orthostatic": ortho_latest
    }


@router.get("/athletes/{athlete_id}/orthostatic-tests", response_model=List[OrthostaticTestRecord])
def get_athlete_orthostatic_tests(athlete_id: str, limit: int = 14):
    if athlete_id not in mock_db.athletes:
        raise HTTPException(status_code=404, detail="Atleta no encontrado")
    tests = mock_db.orthostatic_tests.get(athlete_id, [])
    return tests[-limit:]


@router.post("/athletes/{athlete_id}/orthostatic-test", response_model=OrthostaticTestRecord)
def run_orthostatic_test_endpoint(
    athlete_id: str,
    device_name: str = "Polar H10 (Banda ECG)"
):
    import random
    from datetime import datetime, timezone
    if athlete_id not in mock_db.athletes:
        raise HTTPException(status_code=404, detail="Atleta no encontrado")
        
    athlete = mock_db.athletes[athlete_id]
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Generate live realistic response based on athlete's resting HR
    supine_hr = athlete.resting_hr + random.randint(-1, 3)
    stand_peak = supine_hr + random.randint(22, 30)
    stand_avg = supine_hr + random.randint(15, 21)
    
    supine_series = [int(supine_hr + random.randint(-1, 2)) for _ in range(25)]
    stand_series = [int(stand_avg + random.randint(-2, 2)) for _ in range(30)]
    supine_rrs = [float(round(60000.0 / (supine_hr + random.uniform(-2, 2)), 1)) for _ in range(30)]
    stand_rrs = [float(round(60000.0 / (stand_avg + random.uniform(-1, 1)), 1)) for _ in range(30)]
    
    record = evaluate_orthostatic_test(
        athlete_id=athlete_id,
        date_str=date_str,
        supine_hr_series=supine_series,
        supine_rr_ms=supine_rrs,
        stand_peak_hr=stand_peak,
        stand_hr_series=stand_series,
        stand_rr_ms=stand_rrs,
        device_name=device_name
    )
    
    if athlete_id not in mock_db.orthostatic_tests:
        mock_db.orthostatic_tests[athlete_id] = []
    mock_db.orthostatic_tests[athlete_id].append(record)
    
    # Update latest fatigue record with this fresh test
    latest_workload = mock_db.workload_history.get(athlete_id, [])[-1]
    latest_hrv = mock_db.hrv_records.get(athlete_id, [])[-1]
    
    fatigue_record = synthesize_athlete_fatigue(
        athlete_id=athlete_id,
        date_str=date_str,
        orthostatic=record,
        acwr=latest_workload.acwr,
        latest_rmssd=latest_hrv.rmssd,
        baseline_rmssd=latest_hrv.baseline_7d_mean,
        gct_asymmetry_pct=0.8,
        aerobic_decoupling_pct=3.1,
        nocturnal_temp_deviation=0.08
    )
    mock_db.fatigue_history[athlete_id].append(fatigue_record)
    
    return record

