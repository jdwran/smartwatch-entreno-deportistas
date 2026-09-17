import math
import numpy as np
from typing import List, Dict, Optional, Tuple


def calculate_rmssd_from_rr(rr_intervals_ms: List[float]) -> float:
    """
    Computes RMSSD (Root Mean Square of Successive Differences) from R-R intervals in ms.
    Gold standard metric for parasympathetic activity.
    """
    if len(rr_intervals_ms) < 2:
        return 0.0
        
    rr = np.array(rr_intervals_ms, dtype=np.float64)
    diff = np.diff(rr)
    squared_diff = np.square(diff)
    mean_squared_diff = np.mean(squared_diff)
    rmssd = np.sqrt(mean_squared_diff)
    return float(round(rmssd, 2))


def calculate_sdnn_from_rr(rr_intervals_ms: List[float]) -> float:
    """
    Computes SDNN (Standard Deviation of NN intervals) in ms.
    Reflects overall autonomic nervous system variability.
    """
    if len(rr_intervals_ms) < 2:
        return 0.0
    rr = np.array(rr_intervals_ms, dtype=np.float64)
    sdnn = np.std(rr, ddof=1)
    return float(round(sdnn, 2))


def analyze_hrv_readiness(
    current_rmssd: float,
    current_rhr: int,
    baseline_7d_rmssd: List[float],
    baseline_7d_rhr: List[int]
) -> Dict[str, any]:
    """
    Analyzes HRV using ln(RMSSD) and 7-day rolling baseline with SWC (Smallest Worthwhile Change).
    Provides athletic readiness assessment.
    """
    ln_current = round(math.log(max(1.0, current_rmssd)), 2)
    
    if not baseline_7d_rmssd:
        mean_rmssd = current_rmssd
        sd_rmssd = current_rmssd * 0.15
        mean_rhr = current_rhr
    else:
        mean_rmssd = float(np.mean(baseline_7d_rmssd))
        sd_rmssd = float(np.std(baseline_7d_rmssd, ddof=1)) if len(baseline_7d_rmssd) > 1 else current_rmssd * 0.15
        mean_rhr = float(np.mean(baseline_7d_rhr)) if baseline_7d_rhr else current_rhr

    ln_mean = math.log(max(1.0, mean_rmssd))
    ln_sd = max(0.08, sd_rmssd / max(1.0, mean_rmssd))
    
    # SWC = 0.5 * SD
    swc = 0.5 * ln_sd
    swc_lower = round(math.exp(ln_mean - swc), 1)
    swc_upper = round(math.exp(ln_mean + swc), 1)
    
    rhr_diff = current_rhr - mean_rhr
    
    # Classification logic for elite athletes:
    if current_rmssd < swc_lower:
        if rhr_diff >= 3:
            status = "sympathetic_fatigue"
            description = "Fatiga simpática: HRV deprimida y FC de reposo elevada. El sistema nervioso autónomo está bajo estrés elevado."
            readiness_score = max(30, int(65 - (abs(current_rmssd - swc_lower) * 1.5)))
            recommendation = "Sesión de recuperación activa (Z1) o movilidad articular. Evitar series de alta intensidad o umbral."
        else:
            status = "under_recovered"
            description = "Recuperación incompleta: HRV ligeramente baja respecto a la línea base."
            readiness_score = 68
            recommendation = "Entrenamiento aeróbico moderado (Z2). Monitorear sensaciones durante el calentamiento."
    elif current_rmssd > swc_upper:
        if rhr_diff <= -3:
            status = "parasympathetic_saturation"
            description = "Saturación parasimpática: HRV anormalmente alta y bradicardia marcada. Puede indicar fatiga profunda o sobrecarga aguda acumulada."
            readiness_score = 72
            recommendation = "Mantener intensidad media controlada. Precaución con volúmenes extremos."
        else:
            status = "optimal"
            description = "Supercompensación / Adaptación positiva: Gran tono parasimpático y excelente estado autonómico."
            readiness_score = min(98, int(85 + ((current_rmssd - swc_upper) * 0.4)))
            recommendation = "Luz verde total: Día óptimo para entrenamientos de máxima intensidad, intervalos Z4/Z5 o competencia."
    else:
        status = "optimal"
        description = "Línea base óptima: HRV dentro de la banda de cambio mínimo relevante (SWC). Equilibrio autonómico ideal."
        readiness_score = min(95, max(75, int(85 - abs(current_rmssd - mean_rmssd) * 0.5)))
        recommendation = "Capacidad fisiológica adecuada para asimilar la carga programada del día."

    return {
        "rmssd": current_rmssd,
        "ln_rmssd": ln_current,
        "baseline_7d_mean": round(mean_rmssd, 1),
        "baseline_7d_sd": round(sd_rmssd, 1),
        "swc_lower": swc_lower,
        "swc_upper": swc_upper,
        "current_rhr": current_rhr,
        "baseline_rhr": round(mean_rhr, 1),
        "status": status,
        "status_description": description,
        "readiness_score": readiness_score,
        "recommendation": recommendation
    }
