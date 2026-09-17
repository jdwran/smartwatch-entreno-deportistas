import math
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from backend.app.models.schemas import HeartRateZone, AthleteProfile


def calculate_hr_zones(resting_hr: int, max_hr: int) -> List[HeartRateZone]:
    """
    Calculates 5 physiological heart rate zones using the Karvonen (Heart Rate Reserve) formula:
    Target HR = ((HR_max - HR_rest) * %intensity) + HR_rest
    """
    hrr = max_hr - resting_hr
    
    zone_definitions = [
        (1, "Recuperación Activa (Z1)", 0.50, 0.60),
        (2, "Resistencia Aeróbica / Base (Z2)", 0.60, 0.70),
        (3, "Ritmo Tempo / Mixto (Z3)", 0.70, 0.80),
        (4, "Umbral Anaeróbico / Lactato (Z4)", 0.80, 0.90),
        (5, "Potencia Máxima / VO2max (Z5)", 0.90, 1.00),
    ]
    
    zones: List[HeartRateZone] = []
    for z_num, z_name, low_pct, high_pct in zone_definitions:
        min_hr = int(round(resting_hr + (hrr * low_pct)))
        max_zone_hr = int(round(resting_hr + (hrr * high_pct)))
        zones.append(HeartRateZone(
            zone=z_num,
            name=z_name,
            min_hr=min_hr,
            max_hr=max_zone_hr,
            time_in_seconds=0,
            percentage=0.0
        ))
    return zones


def calculate_caloric_expenditure(
    duration_minutes: float,
    avg_hr: float,
    athlete: AthleteProfile
) -> int:
    """
    Calculates metabolic energy expenditure (kcal) based on Keytel et al. (2005) formula:
    Validated for high-performance exercise with HR, VO2max, weight, and age.
    """
    if athlete.gender.lower() == "male":
        # Male formula (Keytel et al. 2005 with VO2max in kJ/min converted to kcal/min):
        cal_per_min = (
            -95.7735 + (
                0.271 * athlete.age + 
                0.394 * athlete.weight_kg + 
                0.404 * athlete.vo2max + 
                0.634 * avg_hr
            )
        ) / 4.184
    else:
        # Female formula (Keytel et al. 2005 with VO2max):
        cal_per_min = (
            -59.3954 + (
                0.274 * athlete.age + 
                0.103 * athlete.weight_kg + 
                0.380 * athlete.vo2max + 
                0.450 * avg_hr
            )
        ) / 4.184
    
    total_kcal = max(0.0, cal_per_min * duration_minutes)
    return int(round(total_kcal))


def calculate_edwards_trimp(hr_stream: List[int], resting_hr: int, max_hr: int, sample_interval_seconds: int = 1) -> Tuple[float, List[HeartRateZone]]:
    """
    Calculates Edwards TRIMP (Training Impulse) from continuous second-by-second or sampled heart rate stream.
    Weighting factors:
    50-60% HRmax -> 1
    60-70% HRmax -> 2
    70-80% HRmax -> 3
    80-90% HRmax -> 4
    90-100% HRmax -> 5
    """
    zones = calculate_hr_zones(resting_hr, max_hr)
    if not hr_stream:
        return 0.0, zones
        
    zone_seconds = [0, 0, 0, 0, 0]
    
    for hr in hr_stream:
        assigned = False
        for i, z in enumerate(zones):
            if z.min_hr <= hr <= z.max_hr:
                zone_seconds[i] += sample_interval_seconds
                assigned = True
                break
        if not assigned:
            if hr < zones[0].min_hr:
                zone_seconds[0] += sample_interval_seconds
            else:
                zone_seconds[4] += sample_interval_seconds
                
    total_seconds = max(1, sum(zone_seconds))
    for i, z in enumerate(zones):
        z.time_in_seconds = zone_seconds[i]
        z.percentage = round((zone_seconds[i] / total_seconds) * 100, 1)
        
    trimp = (
        (zone_seconds[0] / 60.0) * 1.0 +
        (zone_seconds[1] / 60.0) * 2.0 +
        (zone_seconds[2] / 60.0) * 3.0 +
        (zone_seconds[3] / 60.0) * 4.0 +
        (zone_seconds[4] / 60.0) * 5.0
    )
    
    return round(trimp, 1), zones


def calculate_banister_trimp(
    duration_minutes: float,
    avg_hr: float,
    resting_hr: int,
    max_hr: int,
    gender: str = "male"
) -> float:
    """
    Banister TRIMP (exponential model based on fractional elevation in HR):
    TRIMP = Duration * DeltaHR * 0.64 * e^(b * DeltaHR)
    where b = 1.92 for males and 1.67 for females
    DeltaHR = (HR_avg - HR_rest) / (HR_max - HR_rest)
    """
    if max_hr <= resting_hr:
        return 0.0
    delta_hr = max(0.0, min(1.0, (avg_hr - resting_hr) / (max_hr - resting_hr)))
    b = 1.92 if gender.lower() == "male" else 1.67
    trimp = duration_minutes * delta_hr * 0.64 * math.exp(b * delta_hr)
    return round(trimp, 1)


def calculate_acwr_series(daily_loads: List[Dict[str, float]]) -> List[Dict[str, any]]:
    """
    Computes rolling Acute:Chronic Workload Ratio (ACWR).
    - Acute Load: 7-day average of daily TRIMP
    - Chronic Load: 28-day average of daily TRIMP
    - ACWR = Acute / Chronic
    Optimal zone: 0.8 - 1.3
    Caution: 1.3 - 1.5
    Danger / High Risk: > 1.5
    Underloading: < 0.8
    """
    if not daily_loads:
        return []
        
    results = []
    loads = [d.get("daily_trimp", 0.0) for d in daily_loads]
    
    for i in range(len(daily_loads)):
        # 7-day acute window
        acute_window = loads[max(0, i - 6):i + 1]
        acute_load = sum(acute_window) / len(acute_window)
        
        # 28-day chronic window
        chronic_window = loads[max(0, i - 27):i + 1]
        chronic_load = sum(chronic_window) / len(chronic_window)
        
        acwr = round(acute_load / chronic_load, 2) if chronic_load > 0 else 1.0
        
        if acwr < 0.8:
            zone = "Baja Carga / Desentrenamiento"
        elif 0.8 <= acwr <= 1.3:
            zone = "Óptimo (Zona de Alto Rendimiento)"
        elif 1.3 < acwr <= 1.5:
            zone = "Precaución (Sobrecarga Rápida)"
        else:
            zone = "Alto Riesgo (Peligro de Lesión/Sobreentrenamiento)"
            
        results.append({
            "date": daily_loads[i].get("date"),
            "daily_trimp": round(loads[i], 1),
            "acute_load": round(acute_load, 1),
            "chronic_load": round(chronic_load, 1),
            "acwr": acwr,
            "zone_category": zone
        })
        
    return results
