from typing import Dict, List, Any
from backend.app.models.schemas import SleepStage


def evaluate_sleep_architecture(
    total_sleep_minutes: int,
    time_in_bed_minutes: int,
    deep_minutes: int,
    rem_minutes: int,
    light_minutes: int,
    awake_minutes: int,
    nocturnal_rhr: int,
    daytime_rhr: int,
    target_sleep_minutes: int = 480  # 8 hours for elite athletes
) -> Dict[str, Any]:
    """
    Evaluates elite athlete sleep architecture, restorative sleep ratio, and nocturnal autonomic dip.
    """
    if time_in_bed_minutes <= 0:
        time_in_bed_minutes = max(1, total_sleep_minutes + awake_minutes)
        
    efficiency = round((total_sleep_minutes / time_in_bed_minutes) * 100, 1)
    
    deep_pct = round((deep_minutes / max(1, total_sleep_minutes)) * 100, 1)
    rem_pct = round((rem_minutes / max(1, total_sleep_minutes)) * 100, 1)
    light_pct = round((light_minutes / max(1, total_sleep_minutes)) * 100, 1)
    awake_pct = round((awake_minutes / max(1, time_in_bed_minutes)) * 100, 1)
    
    # Restorative sleep is Deep + REM
    restorative_minutes = deep_minutes + rem_minutes
    restorative_pct = round((restorative_minutes / max(1, total_sleep_minutes)) * 100, 1)
    
    # Nocturnal HR Dip
    if daytime_rhr > 0:
        hr_dip = round(((daytime_rhr - nocturnal_rhr) / daytime_rhr) * 100, 1)
    else:
        hr_dip = 12.0
        
    # Dip classification
    if hr_dip >= 10.0:
        dip_status = "Dipper Fisiológico Óptimo (Recuperación Cardiovascular Adecuada)"
    elif 5.0 <= hr_dip < 10.0:
        dip_status = "Dipper Atenuado (Sobrecarga Metabólica o Estrés Residual)"
    else:
        dip_status = "Non-Dipper (Alerta: Sistema Nervioso Simpático Activo en la Noche)"
        
    # Sleep Score calculation:
    # 1. Duration score (max 35 pts)
    duration_factor = min(1.0, total_sleep_minutes / target_sleep_minutes)
    duration_score = 35 * duration_factor
    
    # 2. Restorative sleep proportion (max 30 pts) - Target is 40-50% Deep+REM
    restorative_factor = min(1.0, restorative_pct / 42.0)
    restorative_score = 30 * restorative_factor
    
    # 3. Efficiency score (max 20 pts) - Target is > 88%
    eff_factor = min(1.0, max(0.0, (efficiency - 60) / 30.0))
    efficiency_score = 20 * eff_factor
    
    # 4. Cardiovascular recovery / HR Dip (max 15 pts)
    dip_factor = min(1.0, max(0.0, hr_dip / 15.0))
    dip_score = 15 * dip_factor
    
    total_score = int(round(duration_score + restorative_score + efficiency_score + dip_score))
    total_score = max(20, min(100, total_score))
    
    stages = [
        SleepStage(stage="deep", minutes=deep_minutes, percentage=deep_pct),
        SleepStage(stage="rem", minutes=rem_minutes, percentage=rem_pct),
        SleepStage(stage="light", minutes=light_minutes, percentage=light_pct),
        SleepStage(stage="awake", minutes=awake_minutes, percentage=awake_pct)
    ]
    
    sleep_debt_minutes = max(0, target_sleep_minutes - total_sleep_minutes)
    
    return {
        "total_sleep_minutes": total_sleep_minutes,
        "time_in_bed_minutes": time_in_bed_minutes,
        "efficiency_percentage": efficiency,
        "deep_minutes": deep_minutes,
        "deep_percentage": deep_pct,
        "rem_minutes": rem_minutes,
        "rem_percentage": rem_pct,
        "light_minutes": light_minutes,
        "light_percentage": light_pct,
        "awake_minutes": awake_minutes,
        "awake_percentage": awake_pct,
        "restorative_minutes": restorative_minutes,
        "restorative_percentage": restorative_pct,
        "nocturnal_rhr": nocturnal_rhr,
        "daytime_rhr": daytime_rhr,
        "hr_dip_percentage": hr_dip,
        "dip_status": dip_status,
        "sleep_score": total_score,
        "sleep_debt_minutes": sleep_debt_minutes,
        "stages": stages
    }
