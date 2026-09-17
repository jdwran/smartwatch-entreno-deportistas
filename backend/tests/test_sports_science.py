import math
import pytest
from backend.app.models.schemas import AthleteProfile
from backend.app.sports_science.energy_engine import (
    calculate_hr_zones,
    calculate_caloric_expenditure,
    calculate_edwards_trimp,
    calculate_banister_trimp,
    calculate_acwr_series
)
from backend.app.sports_science.hrv_engine import (
    calculate_rmssd_from_rr,
    calculate_sdnn_from_rr,
    analyze_hrv_readiness
)
from backend.app.sports_science.sleep_engine import evaluate_sleep_architecture


@pytest.fixture
def sample_athlete():
    return AthleteProfile(
        id="test-ath",
        name="Test Athlete",
        sport="Triathlon",
        age=30,
        gender="male",
        weight_kg=72.0,
        height_cm=180.0,
        resting_hr=45,
        max_hr=195,
        vo2max=65.0
    )


def test_hr_zones_calculation(sample_athlete):
    zones = calculate_hr_zones(sample_athlete.resting_hr, sample_athlete.max_hr)
    assert len(zones) == 5
    # Z1 low should be 50% HRR + resting_hr
    # HRR = 195 - 45 = 150. 50% = 75. 45 + 75 = 120.
    assert zones[0].min_hr == 120
    # Z5 max should be 195
    assert zones[4].max_hr == 195
    # Verify monotonic ordering
    for i in range(len(zones) - 1):
        assert zones[i].min_hr < zones[i+1].min_hr


def test_caloric_expenditure(sample_athlete):
    # 60 minutes at average HR 150 bpm
    calories = calculate_caloric_expenditure(60.0, 150.0, sample_athlete)
    # Expected burn for an endurance athlete at 150 bpm is approximately 700-900 kcal
    assert 600 < calories < 1100


def test_edwards_trimp(sample_athlete):
    # 60 minutes of HR at 160 bpm (which falls in Z3/Z4)
    hr_stream = [160] * 3600
    trimp, zones = calculate_edwards_trimp(hr_stream, sample_athlete.resting_hr, sample_athlete.max_hr)
    assert trimp > 0
    total_pct = sum(z.percentage for z in zones)
    assert 99.0 <= total_pct <= 101.0


def test_banister_trimp(sample_athlete):
    trimp = calculate_banister_trimp(60.0, 150.0, sample_athlete.resting_hr, sample_athlete.max_hr, "male")
    assert trimp > 50.0
    # Higher average HR must produce strictly higher TRIMP
    higher_trimp = calculate_banister_trimp(60.0, 175.0, sample_athlete.resting_hr, sample_athlete.max_hr, "male")
    assert higher_trimp > trimp


def test_acwr_series():
    # 30 days of consistent training
    daily_loads = [{"date": f"2026-09-{i+1:02d}", "daily_trimp": 100.0} for i in range(30)]
    acwr_data = calculate_acwr_series(daily_loads)
    assert len(acwr_data) == 30
    # With steady loads, ACWR should converge to 1.0 (Optimal)
    assert acwr_data[-1]["acwr"] == 1.0
    assert "Óptimo" in acwr_data[-1]["zone_category"]
    
    # Spike on the last 3 days
    daily_loads_spike = [{"date": f"2026-09-{i+1:02d}", "daily_trimp": 100.0} for i in range(27)]
    for i in range(27, 30):
        daily_loads_spike.append({"date": f"2026-09-{i+1:02d}", "daily_trimp": 350.0})
    spike_acwr = calculate_acwr_series(daily_loads_spike)
    assert spike_acwr[-1]["acwr"] > 1.3


def test_rmssd_calculation():
    # Known RR interval differences in ms
    rr = [1000.0, 1050.0, 1000.0, 1060.0, 1010.0]
    rmssd = calculate_rmssd_from_rr(rr)
    # diffs: +50, -50, +60, -50 -> squares: 2500, 2500, 3600, 2500 -> sum=11100 / 4 = 2775 -> sqrt=52.68
    assert math.isclose(rmssd, 52.68, abs_tol=0.2)


def test_hrv_readiness_analysis():
    baseline_rmssd = [80.0, 82.0, 79.0, 81.0, 80.0, 83.0, 81.0]
    baseline_rhr = [42, 43, 42, 41, 42, 43, 42]
    
    # 1. Normal day
    res_opt = analyze_hrv_readiness(81.0, 42, baseline_rmssd, baseline_rhr)
    assert res_opt["status"] == "optimal"
    assert res_opt["readiness_score"] >= 75
    
    # 2. Severe drop with elevated RHR -> sympathetic fatigue
    res_fatigue = analyze_hrv_readiness(55.0, 48, baseline_rmssd, baseline_rhr)
    assert res_fatigue["status"] == "sympathetic_fatigue"
    assert res_fatigue["readiness_score"] < 70


def test_sleep_architecture():
    eval_result = evaluate_sleep_architecture(
        total_sleep_minutes=480,
        time_in_bed_minutes=520,
        deep_minutes=110,
        rem_minutes=110,
        light_minutes=260,
        awake_minutes=40,
        nocturnal_rhr=38,
        daytime_rhr=45
    )
    assert eval_result["efficiency_percentage"] > 90.0
    assert eval_result["hr_dip_percentage"] >= 10.0
    assert eval_result["sleep_score"] >= 85
    assert len(eval_result["stages"]) == 4
