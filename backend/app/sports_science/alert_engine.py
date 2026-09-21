import uuid
from datetime import datetime, timezone
from typing import List, Optional
from backend.app.models.schemas import (
    PhysiologicalAlert,
    AthleteProfile,
    DailyReadiness,
    HRVReading,
    SleepRecord,
    WorkloadDay,
    OrthostaticTestRecord,
    FatigueAnalysis
)


def evaluate_athlete_alerts(
    athlete: AthleteProfile,
    date_str: str,
    readiness: Optional[DailyReadiness],
    workload: Optional[WorkloadDay],
    latest_hrv: Optional[HRVReading],
    latest_sleep: Optional[SleepRecord],
    latest_ortho: Optional[OrthostaticTestRecord],
    fatigue: Optional[FatigueAnalysis]
) -> List[PhysiologicalAlert]:
    """
    Evaluates real-time physiological conditions and detects alarming or abnormal biometric states.
    Categorizes into CRITICAL, HIGH, WARNING, and INFO severity levels.
    """
    alerts: List[PhysiologicalAlert] = []
    now = datetime.now(timezone.utc)

    # -------------------------------------------------------------
    # 1. Alerta de Temperatura Basal / Infección (Oura Ring)
    # -------------------------------------------------------------
    temp_dev = fatigue.nocturnal_temp_deviation if fatigue else None
    if temp_dev is not None:
        if temp_dev >= 0.5:
            alerts.append(PhysiologicalAlert(
                id=f"alt-{uuid.uuid4().hex[:8]}",
                athlete_id=athlete.id,
                timestamp=now,
                date=date_str,
                severity="CRITICAL",
                category="METABOLIC_TEMP",
                title="Alerta Médica: Posible Fiebre / Infección Sistémica Inminente",
                description=f"Elevación térmica nocturna de +{temp_dev}°C sobre la línea base. Sugiere proceso infeccioso activo o hiperinflamación.",
                trigger_metric="Desviación de Temperatura Nocturna (ΔT)",
                trigger_value=f"+{temp_dev} °C",
                threshold="+0.5 °C",
                device_source="Oura Ring Gen 3 (Sensor Térmico NTC)",
                action_required="Aislar al atleta, suspender de inmediato el entrenamiento programado y monitorizar temperatura axilar.",
                acknowledged=False
            ))
        elif temp_dev >= 0.3:
            alerts.append(PhysiologicalAlert(
                id=f"alt-{uuid.uuid4().hex[:8]}",
                athlete_id=athlete.id,
                timestamp=now,
                date=date_str,
                severity="WARNING",
                category="METABOLIC_TEMP",
                title="Alerta Térmica: Inflamación Metabólica Elevada",
                description=f"Incremento moderado de temperatura corporal (+{temp_dev}°C). Posible inicio de sobreentrenamiento o respuesta inmunológica.",
                trigger_metric="Desviación de Temperatura (ΔT)",
                trigger_value=f"+{temp_dev} °C",
                threshold="+0.3 °C",
                device_source="Oura Ring Gen 3",
                action_required="Vigilar sensaciones, asegurar aporte calórico e hidratación y reducir volumen si hay pesadez muscular.",
                acknowledged=False
            ))

    # -------------------------------------------------------------
    # 2. Alerta de Asimetría Biomecánica / Riesgo de Rotura (Garmin HRM-Pro)
    # -------------------------------------------------------------
    asymmetry = fatigue.gct_asymmetry_pct if fatigue else None
    if asymmetry is not None:
        if asymmetry >= 2.5:
            alerts.append(PhysiologicalAlert(
                id=f"alt-{uuid.uuid4().hex[:8]}",
                athlete_id=athlete.id,
                timestamp=now,
                date=date_str,
                severity="CRITICAL",
                category="NEUROMUSCULAR",
                title="Riesgo Inminente de Lesión: Asimetría Biomecánica Severa",
                description=f"Desbalance en el tiempo de contacto con el suelo del {asymmetry}% (ej. 51.3% / 48.7%). El deportista está cojeando o sobrecargando una extremidad.",
                trigger_metric="Asimetría GCT Balance (% Izq/Der)",
                trigger_value=f"{asymmetry} %",
                threshold="2.5 %",
                device_source="Garmin HRM-Pro Plus (Dinámica de Carrera)",
                action_required="Suspender inmediatamente carreras a pie. Revisión fisioterapéutica obligatoria de sóleo, tendón de Aquiles e isquiotibial.",
                acknowledged=False
            ))
        elif asymmetry >= 1.6:
            alerts.append(PhysiologicalAlert(
                id=f"alt-{uuid.uuid4().hex[:8]}",
                athlete_id=athlete.id,
                timestamp=now,
                date=date_str,
                severity="HIGH",
                category="NEUROMUSCULAR",
                title="Alerta Biomecánica: Desbalance Muscular Notorio",
                description=f"Asimetría del {asymmetry}% en dinámica de carrera. Fatiga unilateral perceptible en la pierna dominante.",
                trigger_metric="Asimetría GCT Balance",
                trigger_value=f"{asymmetry} %",
                threshold="1.6 %",
                device_source="Garmin HRM-Pro Plus",
                action_required="Limitar intensidades en carrera, incorporar trabajo propioceptivo y masajes de descarga.",
                acknowledged=False
            ))

    # -------------------------------------------------------------
    # 3. Alerta de Carga Peligrosa (ACWR > 1.55)
    # -------------------------------------------------------------
    if workload:
        if workload.acwr >= 1.6:
            alerts.append(PhysiologicalAlert(
                id=f"alt-{uuid.uuid4().hex[:8]}",
                athlete_id=athlete.id,
                timestamp=now,
                date=date_str,
                severity="CRITICAL",
                category="CARDIOVASCULAR",
                title="Zona de Peligro de Lesión: Sobrecarga Aguda Extrema (ACWR)",
                description=f"El ratio de carga aguda:crónica ha alcanzado {workload.acwr} (la fatiga aguda de 7 días supera ampliamente la capacidad aeróbica de 28 días).",
                trigger_metric="Ratio Carga Aguda:Crónica (ACWR)",
                trigger_value=f"{workload.acwr}",
                threshold="1.60",
                device_source="APEX Workload Engine (Multi-Device TRIMP)",
                action_required="Reducir obligatoriamente el volumen en un 40%. Quedan prohibidas sesiones en zona Z4/Z5 hoy.",
                acknowledged=False
            ))
        elif workload.acwr >= 1.45:
            alerts.append(PhysiologicalAlert(
                id=f"alt-{uuid.uuid4().hex[:8]}",
                athlete_id=athlete.id,
                timestamp=now,
                date=date_str,
                severity="HIGH",
                category="CARDIOVASCULAR",
                title="Sobrecarga Rápida: Entrada en Zona de Precaución (ACWR)",
                description=f"ACWR en {workload.acwr}. Pico agudo de carga por encima del Sweet Spot (0.8 - 1.3).",
                trigger_metric="ACWR",
                trigger_value=f"{workload.acwr}",
                threshold="1.45",
                device_source="APEX Workload Engine",
                action_required="Monitorear respuesta cardíaca en calentamiento y evitar añadir volumen extra.",
                acknowledged=False
            ))

    # -------------------------------------------------------------
    # 4. Alerta de Falla Barorrefleja / Test Ortostático (Polar H10 ECG)
    # -------------------------------------------------------------
    if latest_ortho:
        if latest_ortho.delta_hr > 28:
            alerts.append(PhysiologicalAlert(
                id=f"alt-{uuid.uuid4().hex[:8]}",
                athlete_id=athlete.id,
                timestamp=now,
                date=date_str,
                severity="HIGH",
                category="AUTONOMIC",
                title="Taquicardia Ortostática / Estrés Adrenérgico Agudo",
                description=f"Aumento desmedido de FC al ponerse de pie (ΔHR = +{latest_ortho.delta_hr} bpm, pico de {latest_ortho.stand_peak_hr} bpm). Hipovolemia o sobrecarga adrenérgica.",
                trigger_metric="ΔHR Ortostático",
                trigger_value=f"+{latest_ortho.delta_hr} bpm",
                threshold="+28 bpm",
                device_source="Polar H10 (Banda Pectoral ECG)",
                action_required="Protocolo de rehidratación con electrolitos (sodio/potasio). Rodaje suave en Z1 o descanso.",
                acknowledged=False
            ))
        elif latest_ortho.delta_hr < 6:
            alerts.append(PhysiologicalAlert(
                id=f"alt-{uuid.uuid4().hex[:8]}",
                athlete_id=athlete.id,
                timestamp=now,
                date=date_str,
                severity="CRITICAL",
                category="AUTONOMIC",
                title="Agotamiento Vagal Crónico / Respuesta Barorrefleja Abolida",
                description=f"La frecuencia cardíaca no reacciona ante la gravedad (ΔHR = +{latest_ortho.delta_hr} bpm). Estado de fatiga no funcional profunda.",
                trigger_metric="ΔHR Ortostático",
                trigger_value=f"+{latest_ortho.delta_hr} bpm",
                threshold="+6 bpm",
                device_source="Polar H10 (Banda Pectoral ECG)",
                action_required="Parada total de entrenamientos de intensidad durante 48 horas. Evaluación clínica de sobreentrenamiento.",
                acknowledged=False
            ))

    # -------------------------------------------------------------
    # 5. Colapso Severo de HRV RMSSD
    # -------------------------------------------------------------
    if latest_hrv and latest_hrv.baseline_7d_mean > 0:
        ratio = latest_hrv.rmssd / latest_hrv.baseline_7d_mean
        if ratio < 0.60 and latest_hrv.status == "sympathetic_fatigue":
            alerts.append(PhysiologicalAlert(
                id=f"alt-{uuid.uuid4().hex[:8]}",
                athlete_id=athlete.id,
                timestamp=now,
                date=date_str,
                severity="HIGH",
                category="AUTONOMIC",
                title="Colapso del Tono Parasimpático (Depresión Severa de RMSSD)",
                description=f"El RMSSD matutino cayó un {round((1 - ratio) * 100)}% respecto a la línea base de 7 días ({latest_hrv.rmssd} ms vs media de {latest_hrv.baseline_7d_mean} ms).",
                trigger_metric="RMSSD / Línea Base 7d",
                trigger_value=f"{latest_hrv.rmssd} ms",
                threshold=f"< {round(latest_hrv.baseline_7d_mean * 0.6)} ms",
                device_source=latest_hrv.source_device,
                action_required="Día de descarga regenerativa. Priorizar sueño y nutrición antioxidante.",
                acknowledged=False
            ))

    # -------------------------------------------------------------
    # 6. Alerta de Falta de Descenso Cardíaco Nocturno (Non-Dipper)
    # -------------------------------------------------------------
    if latest_sleep:
        if latest_sleep.hr_dip_percentage < 5.0:
            alerts.append(PhysiologicalAlert(
                id=f"alt-{uuid.uuid4().hex[:8]}",
                athlete_id=athlete.id,
                timestamp=now,
                date=date_str,
                severity="WARNING",
                category="SLEEP",
                title="Falta de Descenso Cardíaco Nocturno (Perfil Non-Dipper)",
                description=f"La FC nocturna solo descendió un {latest_sleep.hr_dip_percentage}% respecto a la diurna. El sistema simpático permaneció hiperactivo durante la noche.",
                trigger_metric="Descenso Cardíaco Nocturno (HR Dip)",
                trigger_value=f"{latest_sleep.hr_dip_percentage} %",
                threshold="< 5.0 %",
                device_source=latest_sleep.source_device,
                action_required="Evaluar digestión tardía, temperatura del dormitorio o sobrecarga de cafeína/estimulantes en la tarde.",
                acknowledged=False
            ))

    # -------------------------------------------------------------
    # 7. Alerta de Desacople Aeróbico Crítico (Pw:HR)
    # -------------------------------------------------------------
    decoupling = fatigue.aerobic_decoupling_pct if fatigue else None
    if decoupling is not None and decoupling > 7.5:
        alerts.append(PhysiologicalAlert(
            id=f"alt-{uuid.uuid4().hex[:8]}",
            athlete_id=athlete.id,
            timestamp=now,
            date=date_str,
            severity="HIGH",
            category="CARDIOVASCULAR",
            title="Desacople Aeróbico Crítico (Deriva Cardiovascular Pw:HR)",
            description=f"Deriva cardiovascular del {decoupling}% durante la sesión. Pérdida severa de vatios por latido, agotamiento de glucógeno o estrés térmico.",
            trigger_metric="Deriva Aeróbica (Pw:HR)",
            trigger_value=f"{decoupling} %",
            threshold="> 7.5 %",
            device_source="Potenciómetro + FC (Stryd / Favero)",
            action_required="Revisar estrategia de recarga de hidratos intra-entrenamiento y valorar estado de deshidratación.",
            acknowledged=False
        ))

    return alerts


def generate_simulated_alert(athlete_id: str, scenario: str = "fever") -> PhysiologicalAlert:
    """
    Generates an alarming biometric event on demand for testing alerts, coach triaging, and real-time triggers.
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    alert_id = f"alt-sim-{uuid.uuid4().hex[:8]}"

    if scenario == "fever":
        return PhysiologicalAlert(
            id=alert_id,
            athlete_id=athlete_id,
            timestamp=now,
            date=date_str,
            severity="CRITICAL",
            category="METABOLIC_TEMP",
            title="[SIMULACIÓN] Alerta Médica: Posible Fiebre / Proceso Infeccioso",
            description="Pico térmico nocturno anómalo de +0.65°C sobre la línea base. Compatible con respuesta inflamatoria aguda o viremia en fase prodrómica.",
            trigger_metric="Desviación de Temperatura Nocturna (ΔT)",
            trigger_value="+0.65 °C",
            threshold="+0.50 °C",
            device_source="Oura Ring Gen 3 (Sensor Térmico NTC)",
            action_required="Aislar al atleta del grupo, cancelar sesión de alta intensidad y realizar prueba antigénica / PCR.",
            acknowledged=False
        )
    elif scenario == "gct_asymmetry":
        return PhysiologicalAlert(
            id=alert_id,
            athlete_id=athlete_id,
            timestamp=now,
            date=date_str,
            severity="CRITICAL",
            category="NEUROMUSCULAR",
            title="[SIMULACIÓN] Riesgo de Rotura Muscular: Asimetría GCT Extrema",
            description="Desbalance del 3.2% en el tiempo de contacto con el suelo (51.6% Izq vs 48.4% Der). El deportista está descargando peso para eludir dolor.",
            trigger_metric="Asimetría Dinámica GCT",
            trigger_value="3.20 %",
            threshold="2.50 %",
            device_source="Garmin HRM-Pro Plus (Dinámica de Carrera)",
            action_required="Detener la sesión de carrera inmediatamente. Evaluación ecográfica urgente de gemelo y tendón rotuliano.",
            acknowledged=False
        )
    elif scenario == "acwr_danger":
        return PhysiologicalAlert(
            id=alert_id,
            athlete_id=athlete_id,
            timestamp=now,
            date=date_str,
            severity="CRITICAL",
            category="CARDIOVASCULAR",
            title="[SIMULACIÓN] Zona de Riesgo de Lesión: ACWR 1.68 Crítico",
            description="La carga aguda de 7 días (Fatigue) superó en un 68% la capacidad crónica de 28 días (Fitness). Riesgo de lesión tisular multiplicado por 3.8x.",
            trigger_metric="Ratio Carga Aguda:Crónica (ACWR)",
            trigger_value="1.68",
            threshold="1.60",
            device_source="APEX Workload Engine (TRIMP Multidispositivo)",
            action_required="Prescribir jornada de descarga activa o descanso absoluto. Prohibir sprints e intervalos Z5.",
            acknowledged=False
        )
    elif scenario == "baroreflex_failure":
        return PhysiologicalAlert(
            id=alert_id,
            athlete_id=athlete_id,
            timestamp=now,
            date=date_str,
            severity="CRITICAL",
            category="AUTONOMIC",
            title="[SIMULACIÓN] Falla Barorrefleja / Fatiga Vagal No Funcional",
            description="Respuesta nula al ortostatismo (ΔHR = +2 bpm). La actividad simpática es incapaz de compensar el cambio gravitacional. Sobreentrenamiento profundo.",
            trigger_metric="ΔHR Ortostático",
            trigger_value="+2 bpm",
            threshold="+6 bpm",
            device_source="Polar H10 (Banda Pectoral ECG)",
            action_required="Parada competitiva y de entrenamientos intensos durante al menos 48h. Análisis bioquímico de cortisol y CK.",
            acknowledged=False
        )
    elif scenario == "tachycardia_ortho":
        return PhysiologicalAlert(
            id=alert_id,
            athlete_id=athlete_id,
            timestamp=now,
            date=date_str,
            severity="HIGH",
            category="AUTONOMIC",
            title="[SIMULACIÓN] Taquicardia Ortostática Excesiva",
            description="Aumento abrupto de +34 bpm al ponerse de pie (de 48 a 82 bpm). Hipovolemia severa o sobrecarga adrenérgica.",
            trigger_metric="ΔHR Ortostático",
            trigger_value="+34 bpm",
            threshold="+28 bpm",
            device_source="Polar H10 (Banda Pectoral ECG)",
            action_required="Aportar 750ml de solución salina/electrolítica y demorar la sesión hasta estabilizar la FC ortostática.",
            acknowledged=False
        )
    elif scenario == "rmssd_collapse":
        return PhysiologicalAlert(
            id=alert_id,
            athlete_id=athlete_id,
            timestamp=now,
            date=date_str,
            severity="HIGH",
            category="AUTONOMIC",
            title="[SIMULACIÓN] Colapso Parasimpático Nocturno (RMSSD -48%)",
            description="El valor RMSSD descendió de su línea base de 85 ms a 44 ms. Supresión simpática severa del sistema nervioso autónomo.",
            trigger_metric="RMSSD / Baseline",
            trigger_value="44.2 ms",
            threshold="< 51.0 ms",
            device_source="Whoop 4.0 / Apple Watch",
            action_required="Reducir el volumen programado a sesión regenerativa en Zona 1 (< 65% FC Máx).",
            acknowledged=False
        )
    elif scenario == "aerobic_drift":
        return PhysiologicalAlert(
            id=alert_id,
            athlete_id=athlete_id,
            timestamp=now,
            date=date_str,
            severity="HIGH",
            category="CARDIOVASCULAR",
            title="[SIMULACIÓN] Deriva Cardiovascular Crítica (Pw:HR +8.9%)",
            description="Desacople aeróbico del 8.9% entre potencia desarrollada y frecuencia cardíaca. Ineficiencia metabólica o agotamiento de glucógeno.",
            trigger_metric="Deriva Aeróbica (Pw:HR)",
            trigger_value="8.90 %",
            threshold="> 7.50 %",
            device_source="Stryd / Favero Assioma + Polar H10",
            action_required="Finalizar el entrenamiento de inmediato; valorar deshidratación y déficit de carbohidratos.",
            acknowledged=False
        )
    else:  # non_dipper
        return PhysiologicalAlert(
            id=alert_id,
            athlete_id=athlete_id,
            timestamp=now,
            date=date_str,
            severity="WARNING",
            category="SLEEP",
            title="[SIMULACIÓN] Perfil Cardíaco No Descendente (Non-Dipper Sleep)",
            description="La frecuencia cardíaca solo descendió un 2.1% durante la noche, indicando ausencia de recuperación parasimpática durante el sueño.",
            trigger_metric="Descenso Cardíaco Nocturno",
            trigger_value="2.10 %",
            threshold="< 5.00 %",
            device_source="Apple Watch Ultra 2 (Sensor Óptico Nocturno)",
            action_required="Analizar higiene del sueño, hora de la última comida y temperatura ambiental.",
            acknowledged=False
        )
