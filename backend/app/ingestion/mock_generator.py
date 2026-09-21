import math
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple
from backend.app.models.schemas import (
    AthleteProfile,
    WorkoutSession,
    HRVReading,
    SleepRecord,
    WorkloadDay,
    DailyReadiness,
    ProviderConnection,
    OrthostaticTestRecord,
    FatigueAnalysis,
    FatiguePillars
)
from backend.app.sports_science.fatigue_engine import (
    evaluate_orthostatic_test,
    synthesize_athlete_fatigue
)
from backend.app.sports_science.energy_engine import (
    calculate_hr_zones,
    calculate_edwards_trimp,
    calculate_banister_trimp,
    calculate_caloric_expenditure,
    calculate_acwr_series
)
from backend.app.sports_science.hrv_engine import analyze_hrv_readiness
from backend.app.sports_science.sleep_engine import evaluate_sleep_architecture


ATHLETES: List[AthleteProfile] = [
    AthleteProfile(
        id="ath-01",
        name="Carlos Alarcón",
        sport="Triatlón de Larga Distancia / Ironman",
        age=28,
        gender="male",
        weight_kg=70.5,
        height_cm=181.0,
        resting_hr=42,
        max_hr=194,
        vo2max=68.5
    ),
    AthleteProfile(
        id="ath-02",
        name="Valentina Gómez",
        sport="Ciclismo de Ruta UCI / Contrarreloj",
        age=25,
        gender="female",
        weight_kg=55.8,
        height_cm=167.0,
        resting_hr=44,
        max_hr=191,
        vo2max=64.8
    )
]

CONNECTIONS_STATE: Dict[str, List[ProviderConnection]] = {
    "ath-01": [
        ProviderConnection(
            provider_id="polar_h10",
            name="Polar H10 (Banda Pectoral ECG)",
            connected=True,
            last_sync=datetime.now(timezone.utc) - timedelta(minutes=25),
            account_email="carlos.alarcon@polarflow.com",
            supported_metrics=["Intervalos R-R ECG (1ms)", "Test Ortostático Matutino", "HRV RMSSD Médico", "DFA alpha-1"],
            auth_type="ble_ecg",
            category="chest_strap"
        ),
        ProviderConnection(
            provider_id="garmin_hrm",
            name="Garmin HRM-Pro Plus",
            connected=True,
            last_sync=datetime.now(timezone.utc) - timedelta(hours=2),
            account_email="carlos.alarcon@triatlon-pro.com",
            supported_metrics=["Dinámica de Carrera", "Asimetría GCT Balance (% Izq/Der)", "Oscilación Vertical", "Poder de Zancada"],
            auth_type="ble_ecg",
            category="chest_strap"
        ),
        ProviderConnection(
            provider_id="garmin",
            name="Garmin Forerunner 965",
            connected=True,
            last_sync=datetime.now(timezone.utc) - timedelta(minutes=15),
            account_email="carlos.alarcon@triatlon-pro.com",
            supported_metrics=["Frecuencia Cardíaca 1Hz", "Potencia", "Cadencia", "GPS", "Fases de Sueño", "VO2max"],
            auth_type="oauth2",
            category="smartwatch"
        ),
        ProviderConnection(
            provider_id="oura_ring",
            name="Oura Ring Gen 3 Horizon",
            connected=True,
            last_sync=datetime.now(timezone.utc) - timedelta(hours=4),
            account_email="carlos.alarcon@oura.com",
            supported_metrics=["Temperatura Basal Nocturna (ΔT°)", "HRV Nocturno Continuo", "Eficiencia del Sueño", "Latencia"],
            auth_type="oauth2",
            category="smart_ring"
        ),
        ProviderConnection(
            provider_id="stryd_power",
            name="Stryd Next Gen (Potenciómetro Running)",
            connected=True,
            last_sync=datetime.now(timezone.utc) - timedelta(hours=6),
            account_email="carlos.alarcon@stryd.com",
            supported_metrics=["Potencia de Carrera (Watts)", "Rigidez Elástica Pierna (LSS)", "Desacople Pw:HR"],
            auth_type="ble_ecg",
            category="power_meter"
        ),
        ProviderConnection(
            provider_id="wahoo_tickr",
            name="Wahoo TICKR X",
            connected=False,
            last_sync=None,
            account_email=None,
            supported_metrics=["Memoria de Entrenamiento Offline", "Cadencia", "HRV"],
            auth_type="ble_ecg",
            category="chest_strap"
        ),
        ProviderConnection(
            provider_id="whoop",
            name="Whoop 4.0 Strap",
            connected=False,
            last_sync=None,
            account_email=None,
            supported_metrics=["Recovery Score", "Sleep Architecture", "Day Strain"],
            auth_type="oauth2",
            category="smartwatch"
        ),
        ProviderConnection(
            provider_id="apple_health",
            name="Apple HealthKit / Health Connect",
            connected=False,
            last_sync=None,
            account_email=None,
            supported_metrics=["Actividad Diaria", "Frecuencia Cardíaca en Reposo"],
            auth_type="health_connect",
            category="smartwatch"
        )
    ],
    "ath-02": [
        ProviderConnection(
            provider_id="polar_h10",
            name="Polar H10 (Banda Pectoral ECG)",
            connected=True,
            last_sync=datetime.now(timezone.utc) - timedelta(minutes=10),
            account_email="valentina.gomez@polarflow.com",
            supported_metrics=["Intervalos R-R ECG", "Test Ortostático Matutino", "HRV Alta Resolución"],
            auth_type="ble_ecg",
            category="chest_strap"
        ),
        ProviderConnection(
            provider_id="whoop",
            name="Whoop 4.0 Strap",
            connected=True,
            last_sync=datetime.now(timezone.utc) - timedelta(minutes=8),
            account_email="valentina.gomez@cycling-elite.com",
            supported_metrics=["Recovery Score", "Sleep Architecture", "HRV Nocturno", "Day Strain"],
            auth_type="oauth2",
            category="smartwatch"
        ),
        ProviderConnection(
            provider_id="garmin",
            name="Garmin Edge 840 (Ciclocomputador)",
            connected=True,
            last_sync=datetime.now(timezone.utc) - timedelta(hours=2),
            account_email="valentina.gomez@cycling-elite.com",
            supported_metrics=["Potencia W/kg", "Zonas FC", "Cadencia", "Temperatura", "Archivos FIT"],
            auth_type="oauth2",
            category="smartwatch"
        ),
        ProviderConnection(
            provider_id="favero_assioma",
            name="Favero Assioma DUO (Pedales Potencia)",
            connected=True,
            last_sync=datetime.now(timezone.utc) - timedelta(hours=3),
            account_email="valentina.gomez@cycling-elite.com",
            supported_metrics=["Potencia Izquierda/Derecha Real", "Eficacia de Par (Torque)", "Desacople Pw:HR"],
            auth_type="ble_ecg",
            category="power_meter"
        ),
        ProviderConnection(
            provider_id="oura_ring",
            name="Oura Ring Gen 3",
            connected=True,
            last_sync=datetime.now(timezone.utc) - timedelta(hours=5),
            account_email="valentina.gomez@oura.com",
            supported_metrics=["Temperatura Basal (ΔT°)", "Fases de Sueño", "Recuperación Nocturna"],
            auth_type="oauth2",
            category="smart_ring"
        ),
        ProviderConnection(
            provider_id="apple_health",
            name="Apple HealthKit",
            connected=True,
            last_sync=datetime.now(timezone.utc) - timedelta(hours=5),
            account_email="valen.apple@icloud.com",
            supported_metrics=["Pasos", "Gasto Basal", "Frecuencia Respiratoria"],
            auth_type="health_connect",
            category="smartwatch"
        )
    ]
}


class MockDatabase:
    """In-memory physiological store with pre-generated 30 days of high performance telemetry."""
    def __init__(self):
        self.athletes = {a.id: a for a in ATHLETES}
        self.workouts: Dict[str, List[WorkoutSession]] = {}
        self.sleep_records: Dict[str, List[SleepRecord]] = {}
        self.hrv_records: Dict[str, List[HRVReading]] = {}
        self.workload_history: Dict[str, List[WorkloadDay]] = {}
        self.daily_readiness: Dict[str, List[DailyReadiness]] = {}
        self.orthostatic_tests: Dict[str, List[OrthostaticTestRecord]] = {}
        self.fatigue_history: Dict[str, List[FatigueAnalysis]] = {}
        self.connections = CONNECTIONS_STATE
        
        self._generate_30_day_history()

    def _generate_30_day_history(self):
        now = datetime.now(timezone.utc)
        random.seed(42)  # Deterministic seed for reproducible testing
        
        for athlete_id, athlete in self.athletes.items():
            self.workouts[athlete_id] = []
            self.sleep_records[athlete_id] = []
            self.hrv_records[athlete_id] = []
            daily_trimp_map: List[Dict[str, float]] = []
            
            # Baseline parameters
            base_rmssd = 82.0 if athlete.gender == "male" else 76.0
            base_rhr = athlete.resting_hr
            
            rolling_rmssd_list: List[float] = []
            rolling_rhr_list: List[int] = []
            
            # Generate 30 days chronologically
            for day_offset in range(29, -1, -1):
                day_date = (now - timedelta(days=day_offset)).date()
                date_str = day_date.strftime("%Y-%m-%d")
                
                # Training cycle phase (Week 1: Base, Week 2: Build, Week 3: Peak Overload, Week 4: Taper/Supercomp)
                cycle_day = (30 - day_offset) % 28
                if cycle_day in [6, 13, 20, 27]:
                    # Rest or active recovery day
                    workout_intensity = "rest"
                elif 14 <= cycle_day <= 19:
                    # High overload block
                    workout_intensity = "overload"
                elif 21 <= cycle_day <= 26:
                    # Taper / Peak performance
                    workout_intensity = "taper"
                else:
                    # Normal endurance build
                    workout_intensity = "build"
                    
                # 1. Generate Workouts for the day
                day_trimp_total = 0.0
                if workout_intensity != "rest":
                    num_sessions = 2 if workout_intensity == "overload" and day_offset % 2 == 0 else 1
                    for s_idx in range(num_sessions):
                        session = self._generate_workout_session(athlete, day_date, s_idx, workout_intensity)
                        self.workouts[athlete_id].append(session)
                        day_trimp_total += session.trimp_edwards
                        
                daily_trimp_map.append({
                    "date": date_str,
                    "daily_trimp": day_trimp_total
                })
                
                # 2. Simulate physiological response on HRV & Sleep
                # If high prior load, RMSSD dips and RHR increases slightly
                fatigue_factor = min(1.3, max(0.7, 1.0 - (day_trimp_total / 600.0) + (0.1 if workout_intensity == "taper" else 0.0)))
                
                day_rhr = base_rhr + int(round(random.uniform(-1, 3) + (2 if day_trimp_total > 180 else 0)))
                day_rmssd = round(base_rmssd * fatigue_factor + random.uniform(-4.0, 4.0), 1)
                
                rolling_rmssd_list.append(day_rmssd)
                rolling_rhr_list.append(day_rhr)
                
                window_rmssd = rolling_rmssd_list[-7:]
                window_rhr = rolling_rhr_list[-7:]
                
                hrv_analysis = analyze_hrv_readiness(
                    current_rmssd=day_rmssd,
                    current_rhr=day_rhr,
                    baseline_7d_rmssd=window_rmssd,
                    baseline_7d_rhr=window_rhr
                )
                
                hrv_reading = HRVReading(
                    id=f"hrv-{athlete_id}-{date_str}",
                    athlete_id=athlete_id,
                    timestamp=datetime.combine(day_date, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=6, minutes=30),
                    rmssd=day_rmssd,
                    sdnn=round(day_rmssd * 1.35, 1),
                    ln_rmssd=hrv_analysis["ln_rmssd"],
                    baseline_7d_mean=hrv_analysis["baseline_7d_mean"],
                    baseline_7d_sd=hrv_analysis["baseline_7d_sd"],
                    swc_lower=hrv_analysis["swc_lower"],
                    swc_upper=hrv_analysis["swc_upper"],
                    status=hrv_analysis["status"],
                    source_device="Polar H10 (ECG-Grade)" if athlete.id == "ath-01" else "Whoop 4.0"
                )
                self.hrv_records[athlete_id].append(hrv_reading)
                
                # 3. Sleep Architecture
                total_sleep_m = int(random.gauss(470, 30))  # ~7h50m
                deep_m = int(total_sleep_m * random.uniform(0.20, 0.26))  # SWS
                rem_m = int(total_sleep_m * random.uniform(0.20, 0.25))
                awake_m = int(random.uniform(20, 45))
                light_m = total_sleep_m - (deep_m + rem_m)
                time_in_bed_m = total_sleep_m + awake_m
                nocturnal_rhr = day_rhr - random.randint(5, 8)
                
                sleep_eval = evaluate_sleep_architecture(
                    total_sleep_minutes=total_sleep_m,
                    time_in_bed_minutes=time_in_bed_m,
                    deep_minutes=deep_m,
                    rem_minutes=rem_m,
                    light_minutes=light_m,
                    awake_minutes=awake_m,
                    nocturnal_rhr=nocturnal_rhr,
                    daytime_rhr=day_rhr
                )
                
                sleep_record = SleepRecord(
                    id=f"sleep-{athlete_id}-{date_str}",
                    athlete_id=athlete_id,
                    date=date_str,
                    start_time=datetime.combine(day_date - timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=22, minutes=30),
                    end_time=datetime.combine(day_date, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=6, minutes=45),
                    total_sleep_minutes=sleep_eval["total_sleep_minutes"],
                    time_in_bed_minutes=sleep_eval["time_in_bed_minutes"],
                    efficiency_percentage=sleep_eval["efficiency_percentage"],
                    deep_sleep_minutes=deep_m,
                    rem_sleep_minutes=rem_m,
                    light_sleep_minutes=light_m,
                    awake_minutes=awake_m,
                    stages=sleep_eval["stages"],
                    nocturnal_rhr=nocturnal_rhr,
                    nocturnal_hrv_rmssd=day_rmssd,
                    daytime_rhr_baseline=day_rhr,
                    hr_dip_percentage=sleep_eval["hr_dip_percentage"],
                    sleep_score=sleep_eval["sleep_score"],
                    source_device="Garmin Sleep Engine" if athlete.id == "ath-01" else "Whoop 4.0 Sleep Coach"
                )
                self.sleep_records[athlete_id].append(sleep_record)

            # 4. Workload calculation (ACWR) for all 30 days
            acwr_list = calculate_acwr_series(daily_trimp_map)
            self.workload_history[athlete_id] = [
                WorkloadDay(
                    date=item["date"],
                    daily_trimp=item["daily_trimp"],
                    acute_load=item["acute_load"],
                    chronic_load=item["chronic_load"],
                    acwr=item["acwr"],
                    zone_category=item["zone_category"]
                )
                for item in acwr_list
            ]
            
            # 5. Build combined daily readiness
            self.daily_readiness[athlete_id] = []
            for i, wl in enumerate(self.workload_history[athlete_id]):
                hrv_item = self.hrv_records[athlete_id][i]
                sleep_item = self.sleep_records[athlete_id][i]
                
                combined_score = int(round((hrv_item.status == "optimal" and 85 or 65) * 0.55 + sleep_item.sleep_score * 0.45))
                
                # Recommendation logic
                if wl.acwr > 1.45:
                    rec = "Riesgo de lesión/sobrecarga aguda elevado (ACWR > 1.45). Reducir volumen en un 30% hoy."
                    intensity = "Active Recovery"
                elif hrv_item.status == "sympathetic_fatigue":
                    rec = "Fatiga simpática detectada. Priorizar descanso activo o rodaje suave en Z1/Z2."
                    intensity = "Moderate / Endurance"
                elif combined_score >= 82:
                    rec = "Condición óptima del sistema nervioso y cardiovascular. Luz verde para sesión de alta intensidad o umbral."
                    intensity = "High Intensity / Interval"
                else:
                    rec = "Estado fisiológico estable. Mantener la carga de base aeróbica planificada."
                    intensity = "Moderate / Endurance"
                    
                self.daily_readiness[athlete_id].append(DailyReadiness(
                    date=wl.date,
                    athlete_id=athlete_id,
                    readiness_score=combined_score,
                    hrv_rmssd=hrv_item.rmssd,
                    hrv_ln_rmssd=hrv_item.ln_rmssd,
                    hrv_status=hrv_item.status,
                    sleep_score=sleep_item.sleep_score,
                    acute_load=wl.acute_load,
                    chronic_load=wl.chronic_load,
                    acwr=wl.acwr,
                    training_recommendation=rec,
                    intensity_target=intensity
                ))

            # 6. Generate Orthostatic Tests (ECG Chest Strap) & Fatigue Analysis History
            self.orthostatic_tests[athlete_id] = []
            self.fatigue_history[athlete_id] = []

            for i, wl in enumerate(self.workload_history[athlete_id]):
                hrv_item = self.hrv_records[athlete_id][i]
                day_offset = 29 - i
                cycle_day = (30 - day_offset) % 28

                if 14 <= cycle_day <= 19:
                    phase = "overload"
                elif 21 <= cycle_day <= 26:
                    phase = "taper"
                else:
                    phase = "build"

                # Simulate chest strap ECG metrics
                if phase == "overload":
                    supine_hr = athlete.resting_hr + random.randint(3, 6)
                    supine_rmssd_val = max(35.0, hrv_item.rmssd * 0.8)
                    stand_peak = supine_hr + random.randint(38, 46)
                    stand_avg = supine_hr + random.randint(26, 31)
                    stand_rmssd_val = 14.0
                    asymmetry = round(random.uniform(1.6, 2.4), 2)
                    decoupling = round(random.uniform(5.8, 8.5), 1)
                    temp_dev = round(random.uniform(0.35, 0.55), 2)
                elif phase == "taper":
                    supine_hr = max(38, athlete.resting_hr - random.randint(1, 3))
                    supine_rmssd_val = hrv_item.rmssd * 1.15
                    stand_peak = supine_hr + random.randint(20, 26)
                    stand_avg = supine_hr + random.randint(13, 18)
                    stand_rmssd_val = 38.0
                    asymmetry = round(random.uniform(0.3, 0.7), 2)
                    decoupling = round(random.uniform(1.5, 3.2), 1)
                    temp_dev = round(random.uniform(-0.1, 0.1), 2)
                else:
                    supine_hr = athlete.resting_hr + random.randint(-1, 2)
                    supine_rmssd_val = hrv_item.rmssd
                    stand_peak = supine_hr + random.randint(25, 32)
                    stand_avg = supine_hr + random.randint(16, 22)
                    stand_rmssd_val = 26.0
                    asymmetry = round(random.uniform(0.6, 1.2), 2)
                    decoupling = round(random.uniform(3.0, 4.6), 1)
                    temp_dev = round(random.uniform(0.0, 0.15), 2)

                supine_series = [int(supine_hr + random.randint(-1, 2)) for _ in range(25)]
                stand_series = [int(stand_avg + random.randint(-2, 2)) for _ in range(30)]
                supine_rrs = [float(round(60000.0 / (supine_hr + random.uniform(-2, 2)), 1)) for _ in range(30)]
                stand_rrs = [float(round(60000.0 / (stand_avg + random.uniform(-1, 1)), 1)) for _ in range(30)]

                device_label = "Polar H10 (Banda ECG)" if athlete.id == "ath-01" else "Garmin HRM-Pro Plus"
                ortho_record = evaluate_orthostatic_test(
                    athlete_id=athlete_id,
                    date_str=wl.date,
                    supine_hr_series=supine_series,
                    supine_rr_ms=supine_rrs,
                    stand_peak_hr=stand_peak,
                    stand_hr_series=stand_series,
                    stand_rr_ms=stand_rrs,
                    device_name=device_label
                )
                self.orthostatic_tests[athlete_id].append(ortho_record)

                fatigue_record = synthesize_athlete_fatigue(
                    athlete_id=athlete_id,
                    date_str=wl.date,
                    orthostatic=ortho_record,
                    acwr=wl.acwr,
                    latest_rmssd=hrv_item.rmssd,
                    baseline_rmssd=hrv_item.baseline_7d_mean,
                    gct_asymmetry_pct=asymmetry,
                    aerobic_decoupling_pct=decoupling,
                    nocturnal_temp_deviation=temp_dev
                )
                self.fatigue_history[athlete_id].append(fatigue_record)

    def _generate_workout_session(self, athlete: AthleteProfile, day_date, session_index: int, phase: str) -> WorkoutSession:
        sports_pool = ["cycling", "running", "swimming"] if athlete.id == "ath-01" else ["cycling", "strength", "cycling"]
        sport = sports_pool[session_index % len(sports_pool)]
        
        device_brand = "Garmin" if athlete.id == "ath-01" else "Whoop"
        device_model = "Garmin Forerunner 965" if device_brand == "Garmin" else "Whoop 4.0 Strap"
        
        if phase == "overload":
            duration_minutes = random.choice([75, 90, 110])
            target_avg_hr = int(athlete.resting_hr + (athlete.max_hr - athlete.resting_hr) * random.uniform(0.72, 0.82))
        elif phase == "taper":
            duration_minutes = random.choice([35, 45, 55])
            target_avg_hr = int(athlete.resting_hr + (athlete.max_hr - athlete.resting_hr) * random.uniform(0.60, 0.70))
        else:
            duration_minutes = random.choice([50, 65, 80])
            target_avg_hr = int(athlete.resting_hr + (athlete.max_hr - athlete.resting_hr) * random.uniform(0.65, 0.75))
            
        start_hour = 8 if session_index == 0 else 17
        start_time = datetime.combine(day_date, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=start_hour, minutes=15)
        end_time = start_time + timedelta(minutes=duration_minutes)
        duration_s = duration_minutes * 60
        
        # Synthetic HR stream
        hr_stream: List[int] = []
        for sec in range(0, duration_s, 5):  # every 5 seconds
            variation = math.sin(sec / 180.0) * 12 + random.randint(-4, 4)
            hr_val = int(max(athlete.resting_hr + 20, min(athlete.max_hr - 2, target_avg_hr + variation)))
            hr_stream.append(hr_val)
            
        avg_hr = int(round(sum(hr_stream) / len(hr_stream)))
        max_hr = max(hr_stream)
        
        trimp_edwards, zones = calculate_edwards_trimp(hr_stream, athlete.resting_hr, athlete.max_hr, sample_interval_seconds=5)
        trimp_banister = calculate_banister_trimp(duration_minutes, avg_hr, athlete.resting_hr, athlete.max_hr, athlete.gender)
        calories = calculate_caloric_expenditure(duration_minutes, avg_hr, athlete)
        
        # Distance calculation based on sport
        if sport == "cycling":
            dist = duration_minutes * 520.0  # ~31 km/h
        elif sport == "running":
            dist = duration_minutes * 230.0  # ~4:20 min/km
        elif sport == "swimming":
            dist = duration_minutes * 45.0
        else:
            dist = 0.0
            
        return WorkoutSession(
            id=f"ws-{athlete.id}-{day_date.strftime('%Y%m%d')}-{session_index}",
            athlete_id=athlete.id,
            device_brand=device_brand,
            device_model=device_model,
            sport_type=sport,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_s,
            distance_meters=round(dist, 1),
            avg_hr=avg_hr,
            max_hr=max_hr,
            calories_burned=calories,
            trimp_edwards=trimp_edwards,
            trimp_banister=trimp_banister,
            zones=zones,
            hr_stream_sample=hr_stream[::max(1, len(hr_stream) // 60)],
            source="simulator"
        )


# Global singleton instance
mock_db = MockDatabase()
