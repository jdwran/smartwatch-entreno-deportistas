import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.models.schemas import (
    AthleteProfile,
    WorkloadDay,
    HRVReading,
    SleepRecord,
    OrthostaticTestRecord,
    FatigueAnalysis,
    DailyReadiness
)
from backend.app.sports_science.alert_engine import evaluate_athlete_alerts, generate_simulated_alert
from backend.app.ingestion.mock_generator import mock_db

from backend.app.sports_science.fatigue_engine import evaluate_orthostatic_test, synthesize_athlete_fatigue

client = TestClient(app)

@pytest.fixture
def mock_athlete():
    return AthleteProfile(
        id="test-ath-01",
        name="Test Runner",
        sport="Maratón",
        gender="male",
        age=28,
        weight_kg=65.0,
        height_cm=178,
        resting_hr=42,
        max_hr=192,
        vo2max=74.0
    )


def test_evaluate_fever_alert_critical(mock_athlete):
    fatigue = synthesize_athlete_fatigue(
        athlete_id=mock_athlete.id,
        date_str="2026-09-21",
        orthostatic=None,
        acwr=1.1,
        latest_rmssd=75.0,
        baseline_rmssd=80.0,
        gct_asymmetry_pct=0.5,
        aerobic_decoupling_pct=2.5,
        nocturnal_temp_deviation=0.68  # > 0.5°C critical
    )
    alerts = evaluate_athlete_alerts(
        athlete=mock_athlete,
        date_str="2026-09-21",
        readiness=None,
        workload=None,
        latest_hrv=None,
        latest_sleep=None,
        latest_ortho=None,
        fatigue=fatigue
    )
    assert len(alerts) >= 1
    fever_alert = next((a for a in alerts if a.category == "METABOLIC_TEMP"), None)
    assert fever_alert is not None
    assert fever_alert.severity == "CRITICAL"
    assert "Fiebre" in fever_alert.title
    assert fever_alert.trigger_value == "+0.68 °C"


def test_evaluate_gct_asymmetry_critical(mock_athlete):
    fatigue = synthesize_athlete_fatigue(
        athlete_id=mock_athlete.id,
        date_str="2026-09-21",
        orthostatic=None,
        acwr=1.0,
        latest_rmssd=80.0,
        baseline_rmssd=80.0,
        gct_asymmetry_pct=3.1,  # > 2.5% critical
        aerobic_decoupling_pct=2.0,
        nocturnal_temp_deviation=0.05
    )
    alerts = evaluate_athlete_alerts(
        athlete=mock_athlete,
        date_str="2026-09-21",
        readiness=None,
        workload=None,
        latest_hrv=None,
        latest_sleep=None,
        latest_ortho=None,
        fatigue=fatigue
    )
    asymmetry_alert = next((a for a in alerts if a.category == "NEUROMUSCULAR"), None)
    assert asymmetry_alert is not None
    assert asymmetry_alert.severity == "CRITICAL"
    assert "Asimetría Biomecánica" in asymmetry_alert.title
    assert "Garmin HRM-Pro" in asymmetry_alert.device_source


def test_evaluate_acwr_danger_critical(mock_athlete):
    workload = WorkloadDay(
        date="2026-09-21",
        daily_trimp=160.0,
        acute_load=410.0,
        chronic_load=240.0,
        acwr=1.71,  # > 1.6 critical
        zone_category="danger_overload"
    )
    alerts = evaluate_athlete_alerts(
        athlete=mock_athlete,
        date_str="2026-09-21",
        readiness=None,
        workload=workload,
        latest_hrv=None,
        latest_sleep=None,
        latest_ortho=None,
        fatigue=None
    )
    acwr_alert = next((a for a in alerts if a.category == "CARDIOVASCULAR"), None)
    assert acwr_alert is not None
    assert acwr_alert.severity == "CRITICAL"
    assert "ACWR" in acwr_alert.title


def test_evaluate_orthostatic_baroreflex_failure(mock_athlete):
    ortho = evaluate_orthostatic_test(
        athlete_id=mock_athlete.id,
        date_str="2026-09-21",
        supine_hr_series=[45] * 25,
        supine_rr_ms=[1333.0] * 25,
        stand_peak_hr=49,
        stand_hr_series=[48] * 30,
        stand_rr_ms=[1250.0] * 30,
        device_name="Polar H10"
    )
    alerts = evaluate_athlete_alerts(
        athlete=mock_athlete,
        date_str="2026-09-21",
        readiness=None,
        workload=None,
        latest_hrv=None,
        latest_sleep=None,
        latest_ortho=ortho,
        fatigue=None
    )
    ortho_alert = next((a for a in alerts if a.category == "AUTONOMIC"), None)
    assert ortho_alert is not None
    assert ortho_alert.severity == "CRITICAL"
    assert "Agotamiento Vagal" in ortho_alert.title


def test_generate_simulated_alerts():
    fever_sim = generate_simulated_alert("ath-01", "fever")
    assert fever_sim.severity == "CRITICAL"
    assert fever_sim.category == "METABOLIC_TEMP"
    assert fever_sim.acknowledged is False

    asym_sim = generate_simulated_alert("ath-01", "gct_asymmetry")
    assert asym_sim.severity == "CRITICAL"
    assert asym_sim.category == "NEUROMUSCULAR"

    drift_sim = generate_simulated_alert("ath-01", "aerobic_drift")
    assert drift_sim.severity == "HIGH"
    assert drift_sim.category == "CARDIOVASCULAR"


def test_api_athlete_alerts():
    response = client.get("/api/athletes/ath-01/alerts")
    assert response.status_code == 200
    alerts = response.json()
    assert isinstance(alerts, list)


def test_api_alerts_summary():
    response = client.get("/api/alerts/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_alerts" in data
    assert "unacknowledged_count" in data
    assert "critical_count" in data
    assert "unacknowledged_alerts" in data


def test_api_simulate_and_acknowledge_alert():
    # 1. Simulate alert
    sim_res = client.post("/api/athletes/ath-01/alerts/simulate?scenario=fever")
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    alert_id = sim_data["id"]
    assert sim_data["acknowledged"] is False
    assert sim_data["severity"] == "CRITICAL"

    # 2. Acknowledge alert
    ack_res = client.post(f"/api/alerts/{alert_id}/acknowledge")
    assert ack_res.status_code == 200
    ack_data = ack_res.json()
    assert ack_data["id"] == alert_id
    assert ack_data["acknowledged"] is True
