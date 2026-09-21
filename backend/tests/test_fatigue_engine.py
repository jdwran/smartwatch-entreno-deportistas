import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.sports_science.fatigue_engine import (
    evaluate_orthostatic_test,
    calculate_aerobic_decoupling,
    calculate_neuromuscular_asymmetry,
    synthesize_athlete_fatigue
)

client = TestClient(app)


def test_orthostatic_optimal_adaptation():
    # Normal response: supine 45 bpm, stand 62 bpm (delta 17 bpm, optimal)
    supine_hrs = [44, 45, 46, 45, 44] * 5
    stand_hrs = [61, 62, 63, 62, 61] * 6
    supine_rrs = [1333.0, 1300.0, 1330.0, 1350.0, 1310.0] * 6
    stand_rrs = [980.0, 945.0, 975.0, 935.0, 965.0] * 6

    res = evaluate_orthostatic_test(
        athlete_id="test-ath",
        date_str="2026-09-21",
        supine_hr_series=supine_hrs,
        supine_rr_ms=supine_rrs,
        stand_peak_hr=72,
        stand_hr_series=stand_hrs,
        stand_rr_ms=stand_rrs
    )
    assert res.status == "optimal_adaptation"
    assert res.delta_hr == 17
    assert res.fatigue_score < 35
    assert len(res.hr_curve) > 20


def test_orthostatic_sympathetic_overdrive():
    # Elevated response: delta_hr > 25 bpm (e.g. supine 48, stand 78 -> delta 30)
    supine_hrs = [48] * 25
    stand_hrs = [78] * 30
    supine_rrs = [1250.0, 1200.0, 1220.0, 1270.0] * 7
    stand_rrs = [769.0, 770.0, 768.0, 771.0] * 7

    res = evaluate_orthostatic_test(
        athlete_id="test-ath",
        date_str="2026-09-21",
        supine_hr_series=supine_hrs,
        supine_rr_ms=supine_rrs,
        stand_peak_hr=96,
        stand_hr_series=stand_hrs,
        stand_rr_ms=stand_rrs
    )
    assert res.status == "sympathetic_overdrive"
    assert res.delta_hr == 30
    assert res.fatigue_score >= 60


def test_orthostatic_parasympathetic_exhaustion():
    # Blunted response: delta_hr < 8 bpm (e.g. supine 44, stand 49 -> delta 5)
    supine_hrs = [44] * 25
    stand_hrs = [49] * 30
    supine_rrs = [1360.0] * 30
    stand_rrs = [1224.0] * 30

    res = evaluate_orthostatic_test(
        athlete_id="test-ath",
        date_str="2026-09-21",
        supine_hr_series=supine_hrs,
        supine_rr_ms=supine_rrs,
        stand_peak_hr=52,
        stand_hr_series=stand_hrs,
        stand_rr_ms=stand_rrs
    )
    assert res.status == "parasympathetic_exhaustion"
    assert res.delta_hr == 5
    assert res.fatigue_score >= 70


def test_aerobic_decoupling():
    # Constant power 200W, HR increases from 140 to 155 in second half (cardiac drift)
    powers = [200.0] * 200
    hrs = [140] * 100 + [155] * 100
    decoupling = calculate_aerobic_decoupling(powers, hrs)
    # EF1 = 200/140 = 1.428, EF2 = 200/155 = 1.290 -> Decoupling = (1.428 - 1.290)/1.428 = ~9.6%
    assert decoupling > 7.0


def test_neuromuscular_asymmetry():
    asym_normal = calculate_neuromuscular_asymmetry(50.3, 49.7)
    assert asym_normal == 0.6
    asym_fatigued = calculate_neuromuscular_asymmetry(51.8, 48.2)
    assert asym_fatigued == 3.6


def test_synthesize_athlete_fatigue():
    # Rested athlete
    fatigue = synthesize_athlete_fatigue(
        athlete_id="ath-01",
        date_str="2026-09-21",
        orthostatic=None,
        acwr=1.0,
        latest_rmssd=85.0,
        baseline_rmssd=85.0,
        gct_asymmetry_pct=0.4,
        aerobic_decoupling_pct=2.1,
        nocturnal_temp_deviation=0.0
    )
    assert fatigue.overall_fatigue_score <= 35
    assert fatigue.fatigue_state in ["Fresco / Óptimo", "Fatiga Funcional"]


def test_api_fatigue_endpoints():
    # Test GET /api/athletes/ath-01/fatigue
    res = client.get("/api/athletes/ath-01/fatigue")
    assert res.status_code == 200
    data = res.json()
    assert "current" in data
    assert "pillars" in data["current"]
    assert "overall_fatigue_score" in data["current"]
    assert len(data["history"]) > 0

    # Test GET /api/athletes/ath-01/orthostatic-tests
    res_ortho = client.get("/api/athletes/ath-01/orthostatic-tests")
    assert res_ortho.status_code == 200
    tests = res_ortho.json()
    assert len(tests) > 0
    assert "delta_hr" in tests[0]
    assert "hr_curve" in tests[0]

    # Test POST /api/athletes/ath-01/orthostatic-test
    res_post = client.post("/api/athletes/ath-01/orthostatic-test?device_name=Polar%20H10")
    assert res_post.status_code == 200
    new_test = res_post.json()
    assert new_test["device_name"] == "Polar H10"
    assert new_test["delta_hr"] > 0
