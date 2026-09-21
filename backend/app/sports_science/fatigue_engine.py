import math
import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from backend.app.models.schemas import (
    OrthostaticTestRecord,
    FatiguePillars,
    FatigueAnalysis,
    AthleteProfile
)
from backend.app.sports_science.hrv_engine import calculate_rmssd_from_rr


def evaluate_orthostatic_test(
    athlete_id: str,
    date_str: str,
    supine_hr_series: List[int],
    supine_rr_ms: List[float],
    stand_peak_hr: int,
    stand_hr_series: List[int],
    stand_rr_ms: List[float],
    device_name: str = "Polar H10 (ECG Grade)"
) -> OrthostaticTestRecord:
    """
    Evaluates an Orthostatic Test (gold standard test for autonomic nervous system fatigue using ECG chest straps).
    - Phase 1: Supine (lying down 3 min) -> tests baseline parasympathetic tone.
    - Phase 2: Postural transition -> tests acute baroreflex responsiveness.
    - Phase 3: Standing (3 min) -> tests orthostatic cardiovascular regulation.
    """
    supine_avg_hr = int(round(float(np.mean(supine_hr_series)))) if supine_hr_series else 45
    supine_rmssd = calculate_rmssd_from_rr(supine_rr_ms) if supine_rr_ms else 85.0

    stand_avg_hr = int(round(float(np.mean(stand_hr_series)))) if stand_hr_series else 62
    stand_rmssd = calculate_rmssd_from_rr(stand_rr_ms) if stand_rr_ms else 35.0

    delta_hr = stand_avg_hr - supine_avg_hr
    delta_rmssd_pct = round(((stand_rmssd - supine_rmssd) / max(1.0, supine_rmssd)) * 100, 1)

    # Build representative full timeline curve (20 points supine, 5 points transition peak, 25 points standing)
    curve: List[int] = []
    for hr in supine_hr_series[-20:]:
        curve.append(hr)
    # transition to peak
    mid_step = int((supine_avg_hr + stand_peak_hr) / 2)
    curve.extend([mid_step, stand_peak_hr, int((stand_peak_hr + stand_avg_hr) / 2)])
    for hr in stand_hr_series[:22]:
        curve.append(hr)

    # Autonomic Classification
    if delta_hr > 25 or (stand_peak_hr - supine_avg_hr > 42):
        status = "sympathetic_overdrive"
        status_label = "Fatiga Simpática / Estrés Adrenérgico"
        fatigue_level = "Alta / Fatiga Adrenérgica"
        fatigue_score = min(92, 60 + int((delta_hr - 25) * 2.5))
        interpretation = (
            f"Incremento postural excesivo (ΔHR = {delta_hr} bpm, pico de {stand_peak_hr} bpm). "
            f"El sistema nervioso simpático está hiperactivado para mantener el gasto cardíaco. "
            f"Indica deshidratación, falta de recuperación glucogénica o sobrecarga aguda elevada."
        )
        recommendation = (
            "Día de descarga: Rodaje suave Z1/Z2 (máx 45 min) o descanso total. Hidratación con electrolitos "
            "y evitar esfuerzos por encima del primer umbral ventilatorio."
        )
    elif delta_hr < 8:
        status = "parasympathetic_exhaustion"
        status_label = "Agotamiento Vagal / Sobreentrenamiento Crónico"
        fatigue_level = "Agotamiento Crónico"
        fatigue_score = min(95, 75 + int((8 - delta_hr) * 3))
        interpretation = (
            f"Respuesta postural atenuada (ΔHR = {delta_hr} bpm). El sistema nervioso no responde a la gravedad; "
            f"los barorreceptores muestran agotamiento y falta de reactividad simpática. Típico de fatiga no funcional acumulada."
        )
        recommendation = (
            "Alerta de sobreentrenamiento: Suspender sesiones intensas. Se recomienda descanso total de 24 a 48 horas "
            "y evaluación médica/fisiológica de fatiga neuroendocrina."
        )
    elif 12 <= delta_hr <= 22 and stand_rmssd >= 15.0:
        status = "optimal_adaptation"
        status_label = "Adaptación Barorrefleja Óptima"
        fatigue_level = "Baja / Fresco"
        fatigue_score = max(10, min(30, 20 + abs(delta_hr - 17)))
        interpretation = (
            f"Transición fisiológica excelente (ΔHR = {delta_hr} bpm, RMSSD supino {supine_rmssd} ms). "
            f"Equilibrio perfecto entre tono vagal y reactividad simpática ortostática."
        )
        recommendation = (
            "Luz verde total: Sistema nervioso y cardiovascular en estado óptimo. Listo para series de máxima intensidad, "
            "competición o test de umbral."
        )
    else:
        status = "functional_fatigue"
        status_label = "Fatiga Funcional Controlada"
        fatigue_level = "Moderada"
        fatigue_score = 45
        interpretation = (
            f"ΔHR postural moderado ({delta_hr} bpm). La respuesta barorrefleja muestra asimilación normal de la carga "
            f"de entrenamiento reciente sin signos de alarma."
        )
        recommendation = "Continuar con el plan programado manteniendo la intensidad controlada."

    return OrthostaticTestRecord(
        id=f"ortho-{athlete_id}-{date_str}",
        athlete_id=athlete_id,
        date=date_str,
        timestamp=datetime.now(timezone.utc),
        device_name=device_name,
        supine_avg_hr=supine_avg_hr,
        supine_rmssd=supine_rmssd,
        stand_peak_hr=stand_peak_hr,
        stand_avg_hr=stand_avg_hr,
        stand_rmssd=stand_rmssd,
        delta_hr=delta_hr,
        delta_rmssd_pct=delta_rmssd_pct,
        status=status,
        status_label=status_label,
        hr_curve=curve,
        fatigue_level=fatigue_level,
        fatigue_score=fatigue_score,
        interpretation=interpretation,
        recommendation=recommendation
    )


def calculate_aerobic_decoupling(
    power_stream: List[float],
    hr_stream: List[int]
) -> float:
    """
    Computes Aerobic Decoupling (Pw:HR or Efficiency Factor drift) in endurance workouts.
    Decoupling > 5.0% signals cardiovascular drift / loss of aerobic efficiency.
    """
    if len(power_stream) < 60 or len(hr_stream) < 60:
        return 0.0

    length = min(len(power_stream), len(hr_stream))
    half = length // 2

    p1 = np.array(power_stream[:half], dtype=float)
    hr1 = np.array(hr_stream[:half], dtype=float)

    p2 = np.array(power_stream[half:length], dtype=float)
    hr2 = np.array(hr_stream[half:length], dtype=float)

    mean_hr1 = np.mean(hr1)
    mean_hr2 = np.mean(hr2)

    if mean_hr1 == 0 or mean_hr2 == 0:
        return 0.0

    ef1 = np.mean(p1) / mean_hr1
    ef2 = np.mean(p2) / mean_hr2

    if ef1 == 0:
        return 0.0

    decoupling_pct = ((ef1 - ef2) / ef1) * 100.0
    return float(round(decoupling_pct, 1))


def calculate_neuromuscular_asymmetry(
    left_balance_pct: float,
    right_balance_pct: float
) -> float:
    """
    Calculates Ground Contact Time (GCT) asymmetry from Garmin HRM-Pro Plus running dynamics.
    Perfect symmetry = 50.0% / 50.0% (diff = 0.0%).
    Asymmetry > 1.5% signals unilateral neuromuscular fatigue or compensation.
    """
    asymmetry = abs(left_balance_pct - right_balance_pct)
    return float(round(asymmetry, 2))


def synthesize_athlete_fatigue(
    athlete_id: str,
    date_str: str,
    orthostatic: Optional[OrthostaticTestRecord],
    acwr: float,
    latest_rmssd: float,
    baseline_rmssd: float,
    gct_asymmetry_pct: Optional[float] = 0.8,
    aerobic_decoupling_pct: Optional[float] = 3.2,
    nocturnal_temp_deviation: Optional[float] = 0.1
) -> FatigueAnalysis:
    """
    Synthesizes multi-sensor fatigue across 4 key physiological pillars:
    1. Autonomic (Orthostatic test & RMSSD baseline deviation)
    2. Cardiovascular (ACWR load ratio & Aerobic decoupling Pw:HR)
    3. Neuromuscular (GCT Balance asymmetry from HRM-Pro)
    4. Metabolic & Thermal (Nocturnal temp from Oura Ring)
    """
    # 1. Autonomic Pillar (0-100)
    if orthostatic:
        autonomic = float(orthostatic.fatigue_score)
    else:
        # Fallback to RMSSD deviation
        diff_pct = (baseline_rmssd - latest_rmssd) / max(1.0, baseline_rmssd)
        autonomic = float(max(15, min(90, int(35 + diff_pct * 100))))

    # 2. Cardiovascular Pillar (0-100)
    # ACWR target is 0.8 - 1.3
    if acwr > 1.5:
        cardio = min(100.0, 70.0 + (acwr - 1.5) * 70.0)
    elif acwr > 1.3:
        cardio = 50.0 + (acwr - 1.3) * 100.0
    else:
        cardio = max(10.0, 20.0 + (aerobic_decoupling_pct or 0.0) * 4.0)

    # 3. Neuromuscular Pillar (0-100)
    asymmetry = gct_asymmetry_pct if gct_asymmetry_pct is not None else 0.6
    if asymmetry > 2.0:
        neuromuscular = min(95.0, 70.0 + (asymmetry - 2.0) * 20.0)
    elif asymmetry > 1.2:
        neuromuscular = 45.0 + (asymmetry - 1.2) * 25.0
    else:
        neuromuscular = 20.0 + asymmetry * 10.0

    # 4. Metabolic / Thermal Pillar (0-100)
    temp_dev = nocturnal_temp_deviation if nocturnal_temp_deviation is not None else 0.0
    if temp_dev > 0.4:
        metabolic = min(100.0, 65.0 + (temp_dev - 0.4) * 80.0)
    elif temp_dev > 0.2:
        metabolic = 40.0 + (temp_dev - 0.2) * 120.0
    else:
        metabolic = 15.0

    pillars = FatiguePillars(
        autonomic=round(autonomic, 1),
        cardiovascular=round(cardio, 1),
        neuromuscular=round(neuromuscular, 1),
        metabolic_temp=round(metabolic, 1)
    )

    # Weighted Composite Score
    # Autonomic 40%, Cardio 25%, Neuromuscular 20%, Metabolic 15%
    overall = int(round(autonomic * 0.40 + cardio * 0.25 + neuromuscular * 0.20 + metabolic * 0.15))
    overall = max(5, min(100, overall))

    # Determine state and primary stressor
    pillar_dict = {
        "Autonómico (Test Ortostático/HRV)": autonomic,
        "Cardiovascular (Carga Aguda/ACWR)": cardio,
        "Neuromuscular (Asimetría Biomecánica)": neuromuscular,
        "Metabólico (Temperatura Corporal/Inflamación)": metabolic
    }
    primary_stressor = max(pillar_dict, key=pillar_dict.get)

    if overall <= 30:
        fatigue_state = "Fresco / Óptimo"
        state_color = "emerald"
        rec = "Nivel de fatiga mínimo. Sistema neuro-cardiovascular totalmente regenerado y disponible para máxima exigencia."
    elif overall <= 55:
        fatigue_state = "Fatiga Funcional"
        state_color = "cyan"
        rec = "Fatiga acumulada dentro del rango adaptativo normal. Continuar con la progresión de carga aeróbica planificada."
    elif overall <= 75:
        fatigue_state = "Fatiga Alta / Precaución"
        state_color = "amber"
        rec = f"Fatiga elevada impulsada por el pilar '{primary_stressor}'. Se recomienda recortar volumen un 25-35% o rodaje de recuperación Z1."
    else:
        fatigue_state = "Agotamiento / Sobreentrenamiento"
        state_color = "rose"
        rec = "Alerta crítica de sobreentrenamiento agudo. Descenso obligatorio de carga, descanso total o sesión regenerativa pasiva."

    return FatigueAnalysis(
        athlete_id=athlete_id,
        date=date_str,
        overall_fatigue_score=overall,
        fatigue_state=fatigue_state,
        state_color=state_color,
        primary_stressor=primary_stressor,
        pillars=pillars,
        latest_orthostatic=orthostatic,
        gct_asymmetry_pct=gct_asymmetry_pct,
        aerobic_decoupling_pct=aerobic_decoupling_pct,
        nocturnal_temp_deviation=nocturnal_temp_deviation,
        recommendation=rec
    )
