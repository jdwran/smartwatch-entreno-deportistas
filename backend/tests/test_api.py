import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_list_athletes():
    res = client.get("/api/athletes")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2
    assert data[0]["name"] == "Carlos Alarcón"


def test_get_athlete_readiness():
    res = client.get("/api/athletes/ath-01/readiness")
    assert res.status_code == 200
    data = res.json()
    assert "current" in data
    assert "readiness_score" in data["current"]
    assert "hrv_rmssd" in data["current"]


def test_get_athlete_workouts():
    res = client.get("/api/athletes/ath-01/workouts")
    assert res.status_code == 200
    workouts = res.json()
    assert len(workouts) > 0
    first = workouts[0]
    assert "calories_burned" in first
    assert "trimp_edwards" in first
    assert "zones" in first


def test_get_athlete_sleep():
    res = client.get("/api/athletes/ath-01/sleep")
    assert res.status_code == 200
    data = res.json()
    assert "current" in data
    assert "deep_sleep_minutes" in data["current"]
    assert "hr_dip_percentage" in data["current"]


def test_get_athlete_workload():
    res = client.get("/api/athletes/ath-01/workload")
    assert res.status_code == 200
    data = res.json()
    assert "history" in data
    assert len(data["history"]) == 30
    assert "acwr" in data["history"][-1]


def test_get_integrations_and_toggle():
    res = client.get("/api/athletes/ath-01/integrations")
    assert res.status_code == 200
    integrations = res.json()
    assert len(integrations) >= 4
    
    # Toggle whoop
    toggle_res = client.post("/api/athletes/ath-01/integrations/whoop/toggle")
    assert toggle_res.status_code == 200
    assert toggle_res.json()["provider"]["connected"] is True


def test_upload_sample_fit_file():
    # Simulate an uploaded file
    file_content = b"\x0e\x10\x47\x08.FIT" + b"\x00" * 4000
    res = client.post(
        "/api/upload/fit",
        files={"file": ("garmin_session.fit", file_content, "application/octet-stream")},
        data={"athlete_id": "ath-01"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "workout" in data
    assert data["workout"]["device_brand"] == "Garmin"
