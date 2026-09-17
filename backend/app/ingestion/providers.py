from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from backend.app.models.schemas import (
    WorkoutSession,
    SleepRecord,
    HRVReading,
    AthleteProfile,
    ProviderConnection
)
from backend.app.sports_science.energy_engine import (
    calculate_banister_trimp,
    calculate_caloric_expenditure,
    calculate_hr_zones
)
from backend.app.sports_science.sleep_engine import evaluate_sleep_architecture
from backend.app.sports_science.hrv_engine import analyze_hrv_readiness


class WhoopAdapter:
    """
    Adapter for Whoop Developer API (v1).
    Endpoint structures:
    - GET /v1/recovery -> recovery_score, resting_heart_rate, hrv_rmssd_milli
    - GET /v1/activity/workout -> score (strain, avg_heart_rate, max_heart_rate, kilojoule)
    - GET /v1/activity/sleep -> score (stage_summary: total_in_bed_time_milli, light_sleep_time_milli, slow_wave_sleep_time_milli, rem_sleep_time_milli, awake_time_milli)
    """
    @staticmethod
    def normalize_workout(whoop_payload: Dict[str, Any], athlete: AthleteProfile) -> WorkoutSession:
        start = datetime.fromisoformat(whoop_payload.get("start", datetime.now(timezone.utc).isoformat()))
        end = datetime.fromisoformat(whoop_payload.get("end", (start + timedelta(minutes=60)).isoformat()))
        duration_s = int((end - start).total_seconds())
        
        score = whoop_payload.get("score", {})
        avg_hr = int(score.get("average_heart_rate", 145))
        max_hr = int(score.get("max_heart_rate", 178))
        kj = score.get("kilojoule", 2000.0)
        calories = int(kj / 4.184) if kj else calculate_caloric_expenditure(duration_s / 60.0, avg_hr, athlete)
        
        zones = calculate_hr_zones(athlete.resting_hr, athlete.max_hr)
        # Allocate proportional time across zones based on avg HR
        for z in zones:
            if z.min_hr <= avg_hr <= z.max_hr:
                z.percentage = 45.0
                z.time_in_seconds = int(duration_s * 0.45)
            elif z.zone == 2:
                z.percentage = 35.0
                z.time_in_seconds = int(duration_s * 0.35)
            else:
                z.percentage = 10.0
                z.time_in_seconds = int(duration_s * 0.10)
                
        trimp = calculate_banister_trimp(duration_s / 60.0, avg_hr, athlete.resting_hr, athlete.max_hr, athlete.gender)
        
        return WorkoutSession(
            id=f"whoop-{whoop_payload.get('id', 'sample')}",
            athlete_id=athlete.id,
            device_brand="Whoop",
            device_model="Whoop 4.0",
            sport_type=whoop_payload.get("sport_name", "cross_training").lower(),
            start_time=start,
            end_time=end,
            duration_seconds=duration_s,
            distance_meters=whoop_payload.get("distance_meter"),
            avg_hr=avg_hr,
            max_hr=max_hr,
            calories_burned=calories,
            trimp_edwards=round(trimp * 1.1, 1),
            trimp_banister=trimp,
            zones=zones,
            source="whoop_api"
        )

    @staticmethod
    def normalize_sleep(whoop_sleep_payload: Dict[str, Any], athlete: AthleteProfile) -> SleepRecord:
        stages = whoop_sleep_payload.get("score", {}).get("stage_summary", {})
        total_m = int(stages.get("total_in_bed_time_milli", 28800000) / 60000)
        deep_m = int(stages.get("slow_wave_sleep_time_milli", 6600000) / 60000)
        rem_m = int(stages.get("rem_sleep_time_milli", 6000000) / 60000)
        awake_m = int(stages.get("awake_time_milli", 1800000) / 60000)
        light_m = max(0, total_m - (deep_m + rem_m + awake_m))
        
        recovery = whoop_sleep_payload.get("recovery", {})
        nocturnal_rhr = recovery.get("resting_heart_rate", athlete.resting_hr - 2)
        nocturnal_hrv = recovery.get("hrv_rmssd_milli", 75.0)
        
        arch = evaluate_sleep_architecture(
            total_sleep_minutes=total_m - awake_m,
            time_in_bed_minutes=total_m,
            deep_minutes=deep_m,
            rem_minutes=rem_m,
            light_minutes=light_m,
            awake_minutes=awake_m,
            nocturnal_rhr=nocturnal_rhr,
            daytime_rhr=athlete.resting_hr
        )
        
        date_str = whoop_sleep_payload.get("date", datetime.now().strftime("%Y-%m-%d"))
        return SleepRecord(
            id=f"whoop-sleep-{date_str}",
            athlete_id=athlete.id,
            date=date_str,
            start_time=datetime.now(timezone.utc) - timedelta(hours=8),
            end_time=datetime.now(timezone.utc),
            total_sleep_minutes=arch["total_sleep_minutes"],
            time_in_bed_minutes=arch["time_in_bed_minutes"],
            efficiency_percentage=arch["efficiency_percentage"],
            deep_sleep_minutes=deep_m,
            rem_sleep_minutes=rem_m,
            light_sleep_minutes=light_m,
            awake_minutes=awake_m,
            stages=arch["stages"],
            nocturnal_rhr=nocturnal_rhr,
            nocturnal_hrv_rmssd=nocturnal_hrv,
            daytime_rhr_baseline=athlete.resting_hr,
            hr_dip_percentage=arch["hr_dip_percentage"],
            sleep_score=arch["sleep_score"],
            source_device="Whoop 4.0"
        )


class PolarAdapter:
    """
    Adapter for Polar AccessLink API (v3).
    Endpoint structures:
    - GET /v3/users/{userId}/exercise-transactions/{transactionId}
    - GET /v3/users/{userId}/sleep
    """
    @staticmethod
    def normalize_exercise(polar_exercise: Dict[str, Any], athlete: AthleteProfile) -> WorkoutSession:
        start = datetime.fromisoformat(polar_exercise.get("start_time", datetime.now(timezone.utc).isoformat()))
        duration_s = int(polar_exercise.get("duration", 3600))
        end = start + timedelta(seconds=duration_s)
        
        avg_hr = int(polar_exercise.get("heart_rate", {}).get("average", 152))
        max_hr = int(polar_exercise.get("heart_rate", {}).get("maximum", 182))
        calories = int(polar_exercise.get("kilo_calories", 650))
        distance = float(polar_exercise.get("distance", 15000.0))
        sport = str(polar_exercise.get("sport", "RUNNING")).lower()
        
        trimp = calculate_banister_trimp(duration_s / 60.0, avg_hr, athlete.resting_hr, athlete.max_hr, athlete.gender)
        zones = calculate_hr_zones(athlete.resting_hr, athlete.max_hr)
        
        return WorkoutSession(
            id=f"polar-{polar_exercise.get('id', 'sample')}",
            athlete_id=athlete.id,
            device_brand="Polar",
            device_model=polar_exercise.get("device_name", "Polar Vantage V3"),
            sport_type=sport,
            start_time=start,
            end_time=end,
            duration_seconds=duration_s,
            distance_meters=distance,
            avg_hr=avg_hr,
            max_hr=max_hr,
            calories_burned=calories,
            trimp_edwards=round(trimp * 1.15, 1),
            trimp_banister=trimp,
            zones=zones,
            source="polar_accesslink"
        )


class GarminAdapter:
    """
    Adapter for Garmin Connect Developer Program (Health & Activity API).
    """
    @staticmethod
    def normalize_activity(garmin_payload: Dict[str, Any], athlete: AthleteProfile) -> WorkoutSession:
        start = datetime.fromtimestamp(garmin_payload.get("startTimeInSeconds", datetime.now().timestamp()), tz=timezone.utc)
        duration_s = int(garmin_payload.get("durationInSeconds", 3600))
        end = start + timedelta(seconds=duration_s)
        
        avg_hr = int(garmin_payload.get("averageHeartRateInBeatsPerMinute", 148))
        max_hr = int(garmin_payload.get("maxHeartRateInBeatsPerMinute", 179))
        calories = int(garmin_payload.get("activeKilocalories", 720))
        distance = float(garmin_payload.get("distanceInMeters", 20000.0))
        activity_type = str(garmin_payload.get("activityType", "CYCLING")).lower()
        
        trimp = calculate_banister_trimp(duration_s / 60.0, avg_hr, athlete.resting_hr, athlete.max_hr, athlete.gender)
        zones = calculate_hr_zones(athlete.resting_hr, athlete.max_hr)
        
        return WorkoutSession(
            id=f"garmin-{garmin_payload.get('activityId', 'sample')}",
            athlete_id=athlete.id,
            device_brand="Garmin",
            device_model=garmin_payload.get("deviceName", "Garmin Forerunner 965"),
            sport_type=activity_type,
            start_time=start,
            end_time=end,
            duration_seconds=duration_s,
            distance_meters=distance,
            avg_hr=avg_hr,
            max_hr=max_hr,
            calories_burned=calories,
            trimp_edwards=round(trimp * 1.12, 1),
            trimp_banister=trimp,
            zones=zones,
            source="garmin_connect"
        )
