from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HeartRateZone(BaseModel):
    zone: int
    name: str
    min_hr: int
    max_hr: int
    time_in_seconds: int = 0
    percentage: float = 0.0


class AthleteProfile(BaseModel):
    id: str
    name: str
    sport: str
    age: int
    gender: str = "male"  # "male" or "female"
    weight_kg: float
    height_cm: float
    resting_hr: int = 48
    max_hr: int = 192
    vo2max: float = 62.0


class WorkoutSession(BaseModel):
    id: str
    athlete_id: str
    device_brand: str  # "Garmin", "Polar", "Whoop", "Apple", "Coros", "Wahoo"
    device_model: Optional[str] = None
    sport_type: str  # "cycling", "running", "swimming", "strength", "hiit"
    start_time: datetime
    end_time: datetime
    duration_seconds: int
    distance_meters: Optional[float] = None
    avg_hr: int
    max_hr: int
    calories_burned: int
    trimp_edwards: float
    trimp_banister: float
    zones: List[HeartRateZone] = []
    hr_stream_sample: Optional[List[int]] = None  # Downsampled for visualization
    source: str = "api"  # "api", "fit_file", "manual", "simulator"


class HRVReading(BaseModel):
    id: str
    athlete_id: str
    timestamp: datetime
    rmssd: float
    sdnn: Optional[float] = None
    ln_rmssd: float
    baseline_7d_mean: float
    baseline_7d_sd: float
    swc_lower: float  # Smallest Worthwhile Change lower bound
    swc_upper: float  # Smallest Worthwhile Change upper bound
    status: str  # "optimal", "sympathetic_fatigue", "parasympathetic_saturation", "under_recovered"
    source_device: str


class SleepStage(BaseModel):
    stage: str  # "deep", "rem", "light", "awake"
    minutes: int
    percentage: float


class SleepRecord(BaseModel):
    id: str
    athlete_id: str
    date: str  # YYYY-MM-DD
    start_time: datetime
    end_time: datetime
    total_sleep_minutes: int
    time_in_bed_minutes: int
    efficiency_percentage: float
    deep_sleep_minutes: int
    rem_sleep_minutes: int
    light_sleep_minutes: int
    awake_minutes: int
    stages: List[SleepStage] = []
    nocturnal_rhr: int
    nocturnal_hrv_rmssd: float
    daytime_rhr_baseline: int
    hr_dip_percentage: float  # High performance target: 10% - 20%
    sleep_score: int  # 0 to 100
    source_device: str


class WorkloadDay(BaseModel):
    date: str
    daily_trimp: float
    acute_load: float  # 7-day EWMA / rolling
    chronic_load: float  # 28-day EWMA / rolling
    acwr: float  # Acute:Chronic Workload Ratio
    zone_category: str  # "underloading" (<0.8), "optimal" (0.8-1.3), "caution" (1.3-1.5), "high_risk" (>1.5)


class DailyReadiness(BaseModel):
    date: str
    athlete_id: str
    readiness_score: int  # 0 to 100
    hrv_rmssd: float
    hrv_ln_rmssd: float
    hrv_status: str
    sleep_score: int
    acute_load: float
    chronic_load: float
    acwr: float
    training_recommendation: str
    intensity_target: str  # "Rest", "Active Recovery", "Moderate / Endurance", "High Intensity / Interval", "Overreaching Caution"


class ProviderConnection(BaseModel):
    provider_id: str  # "garmin", "polar", "whoop", "apple_health"
    name: str
    connected: bool
    last_sync: Optional[datetime] = None
    account_email: Optional[str] = None
    supported_metrics: List[str] = []
    auth_type: str  # "oauth2", "webhook", "health_connect", "fit_direct"
