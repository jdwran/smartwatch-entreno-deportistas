# APEX PRO // Plataforma de Telemetría y Biometría Fisiológica para Smartwatches

> Sistema agnóstico para conectar relojes inteligentes (**Garmin, Polar, Whoop, Apple Watch, Wahoo, Coros**) y sintetizar datos para **deportistas de alto rendimiento** y entrenadores:
> - **Gasto Energético & Carga de Entrenamiento**: TRIMP (Edwards & Banister), Zonas FC (Z1-Z5) y Ratio de Carga Aguda:Crónica (**ACWR**).
> - **Variabilidad Cardíaca (HRV)**: RMSSD, lnRMSSD, línea base móvil de 7 días y banda de cambio mínimo relevante (**SWC**).
> - **Arquitectura del Sueño**: Fases (Profundo/SWS, REM, Ligero), Eficiencia, Deuda de Sueño y Descenso Cardíaco Nocturno (*Nocturnal HR Dip*).

---

## 1. Arquitectura de Ingesta Multimarca

Para resolver el reto de conectar "cualquier reloj inteligente" de marcas con ecosistemas dispares:

1. **APIs Cloud (OAuth2 & Webhooks)**:
   - **Whoop Developer API (v1)**: Sincronización directa de ciclos diarios, recuperaciones, sueño por fases y strain.
   - **Polar AccessLink API (v3)**: Ingesta de ejercicios, telemetría cardíaca y transacciones de datos físicos.
   - **Garmin Connect Developer Program**: Receptor de webhooks para cargas de actividades y métricas de salud continuas.
   - **Apple HealthKit / Google Health Connect**: Soporte para agregadores de salud del sistema operativo móvil.

2. **Ingestor Universal Directo de Archivos `.FIT` / `.TCX`**:
   - Módulo binario con decodificación milisegundo a milisegundo.
   - Permite a deportistas y entrenadores arrastrar y soltar cualquier archivo `.fit` extraído de cualquier reloj (Garmin Forerunner/Fenix/Edge, Polar Vantage/Grit, Wahoo BOLT/ROAM, Coros Pace) sin necesidad de permisos empresariales corporativos.

3. **Simulador Fisiológico de Élite (30 Días)**:
   - Base de datos con telemetría de 30 días de bloques de entrenamiento (Fase Base, Sobrecarga, Tapering, Supercompensación) para triatletas y ciclistas UCI.

---

## 2. Modelos Fisiológicos y Fórmulas Matemáticas

### A. Gasto Energético & Carga de Entrenamiento
- **Gasto Calórico Metabólico (Keytel et al., 2005)**:
  $$\text{Hombres: } \text{kJ/min} = -95.7735 + (0.271 \times \text{edad}) + (0.394 \times \text{peso}) + (0.404 \times \text{VO2max}) + (0.634 \times \text{FC})$$
  $$\text{Mujeres: } \text{kJ/min} = -59.3954 + (0.274 \times \text{edad}) + (0.103 \times \text{peso}) + (0.380 \times \text{VO2max}) + (0.450 \times \text{FC})$$
- **TRIMP de Edwards**: Ponderación por zonas cardíacas individuales (Z1 a Z5):
  $$\text{TRIMP}_{Edwards} = \sum_{i=1}^5 (t_{zona\_i} \times i)$$
- **TRIMP de Banister**: Modelo exponencial de impulso de entrenamiento basado en la elevación fraccional de la frecuencia cardíaca de reserva ($\Delta HR$).
- **ACWR (Acute:Chronic Workload Ratio)**:
  $$\text{ACWR} = \frac{\text{Carga Aguda (Media Móvil 7 días)}}{\text{Carga Crónica (Media Móvil 28 días)}}$$
  - $< 0.8$: Desentrenamiento / Carga baja.
  - **$0.8 - 1.3$**: **Zona Óptima de Rendimiento ("Sweet Spot")**.
  - $1.3 - 1.5$: Zona de precaución.
  - $> 1.5$: Zona de alto riesgo de lesión y sobreentrenamiento agudo.

### B. Variabilidad de la Frecuencia Cardíaca (HRV)
- **RMSSD (Root Mean Square of Successive Differences)**: Medida dorada de la actividad parasimpática y modulación vagal.
- **Línea Base Móvil y SWC (Smallest Worthwhile Change)**:
  $$\text{SWC} = \text{Media 7d} \pm (0.5 \times \text{SD 7d})$$
- **Interpretación Autonómica**:
  - *Línea Base Óptima*: Adaptación positiva, luz verde para cargas intensas.
  - *Fatiga Simpática*: RMSSD inferior a la banda SWC con FC reposo elevada.
  - *Saturación Parasimpática*: RMSSD por encima de la banda con bradicardia marcada (sobreentrenamiento profundo).

### C. Arquitectura del Sueño
- **Sueño Profundo (SWS)**: Esencial para la secreción de Hormona del Crecimiento (GH) y reparación celular.
- **Sueño REM**: Consolidación motora, memoria técnica y reflejos neuromusculares.
- **Descenso Cardíaco Nocturno (Nocturnal HR Dip)**:
  $$\text{Dip \%} = \frac{\text{FC Reposo Diurna} - \text{FC Nocturna Mínima}}{\text{FC Reposo Diurna}} \times 100$$
  - Target en deportistas de élite: **$10\% - 20\%$**.

### D. Bandas Cardíacas Pectorales (ECG) & Motor Avanzado de Fatiga

Las bandas pectorales (**Polar H10, Garmin HRM-Pro Plus, Wahoo TICKR X**) registran microvoltajes eléctricos (ECG) con resolución de **1 milisegundo en intervalos R-R**, permitiendo diagnósticos de fatiga inalcanzables con sensores ópticos de muñeca:

1. **Test Ortostático Matutino (Orthostatic Baroreflex Test)**:
   - **Fase Supino (3 min)**: Evaluación del tono parasimpático basal ($\text{FC}_{supino}$, $\text{RMSSD}_{supino}$).
   - **Transición & Pico Postural**: Respuesta barorrefleja aguda ($\text{HR}_{peak}$).
   - **Fase Bipedestación (3 min)**: Activación adrenérgica estabilizada ($\text{HR}_{stand}$, $\Delta\text{HR} = \text{HR}_{stand} - \text{HR}_{supino}$).
   - **Interpretación**:
     - *Adaptación Óptima*: $\Delta\text{HR}$ entre $12$ y $22\text{ bpm}$ y $\text{RMSSD}_{stand} \ge 15\text{ ms}$.
     - *Fatiga Simpática / Estrés Adrenérgico*: $\Delta\text{HR} > 24\text{ bpm}$ o caída de RMSSD $>75\%$ (deshidratación, hipovolemia, sobrecarga aguda).
     - *Agotamiento Vagal / Sobreentrenamiento Crónico*: $\Delta\text{HR} < 8\text{ bpm}$ (falta total de reactividad autonómica).

2. **Matriz de los 4 Pilares de Fatiga Multidispositivo (0 a 100)**:
   - **Pilar Autonómico (40%)**: Banda Polar H10 (Test Ortostático & RMSSD).
   - **Pilar Cardiovascular (25%)**: Stryd / Favero + FC (Desacople aeróbico $Pw:\text{HR} > 5\%$ y ACWR).
   - **Pilar Neuromuscular (20%)**: Garmin HRM-Pro Plus (Asimetría en tiempo de contacto con el suelo $\text{GCT} > 1.5\%$).
   - **Pilar Metabólico/Térmico (15%)**: Oura Ring Gen 3 (Desviación de temperatura basal nocturna $\Delta T^\circ > +0.3^\circ\text{C}$).

---

## 3. Instrucciones de Ejecución

### Requisitos Previos
- Python 3.10+
- Node.js 18+

### 1. Iniciar el Backend (FastAPI)
```powershell
# En la raíz del proyecto:
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH="."
uvicorn backend.main:app --reload --port 8000
```
La documentación interactiva Swagger estará disponible en: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Iniciar el Frontend (React + Vite + Tailwind)
```powershell
cd frontend
npm run dev
```
El panel estará disponible en: [http://localhost:5180](http://localhost:5180)

---

## 4. Ejecución de Pruebas Automatizadas
Para verificar todos los algoritmos fisiológicos y endpoints de la API:
```powershell
$env:PYTHONPATH="."
.\venv\Scripts\pytest backend/tests -v
```
Todos los tests validan cálculos de RMSSD, TRIMP, ACWR, arquitectura de sueño y decodificación `.FIT`.
