import React, { useState } from 'react';
import { FatigueAnalysis, OrthostaticTestRecord } from '../types';
import {
  Activity,
  Heart,
  Zap,
  Flame,
  Thermometer,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCw,
  Watch,
  Footprints,
  Layers
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ReferenceLine,
  ReferenceArea
} from 'recharts';
import { runOrthostaticTest } from '../services/api';

interface FatigueAnalysisViewProps {
  fatigueData: {
    current: FatigueAnalysis | null;
    history: FatigueAnalysis[];
    latest_orthostatic: OrthostaticTestRecord | null;
  };
  athleteId: string;
  onRefresh: () => void;
}

export const FatigueAnalysisView: React.FC<FatigueAnalysisViewProps> = ({
  fatigueData,
  athleteId,
  onRefresh
}) => {
  const [runningTest, setRunningTest] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState('Polar H10 (Banda ECG)');
  const [testSuccessMessage, setTestSuccessMessage] = useState<string | null>(null);

  const current = fatigueData.current;
  const latestOrtho = fatigueData.latest_orthostatic || current?.latest_orthostatic;

  const handleRunLiveTest = async () => {
    try {
      setRunningTest(true);
      setTestSuccessMessage(null);
      const res = await runOrthostaticTest(athleteId, selectedDevice);
      setTestSuccessMessage(`¡Test ortostático registrado exitosamente con ${res.device_name}! ΔHR: +${res.delta_hr} bpm (${res.status_label}).`);
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Error al ejecutar test ortostático');
    } finally {
      setRunningTest(false);
    }
  };

  if (!current) return null;

  // Formatting colors
  let colorBadge = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  let gaugeColor = 'text-emerald-400';
  if (current.overall_fatigue_score > 75) {
    colorBadge = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    gaugeColor = 'text-rose-400';
  } else if (current.overall_fatigue_score > 55) {
    colorBadge = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    gaugeColor = 'text-amber-400';
  } else if (current.overall_fatigue_score > 30) {
    colorBadge = 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
    gaugeColor = 'text-cyan-400';
  }

  // Orthostatic curve formatting
  const orthoChartData = latestOrtho?.hr_curve.map((hr, idx) => {
    let phase = 'Supino (Acostado)';
    if (idx >= 20 && idx <= 23) phase = 'Transición Postural';
    else if (idx > 23) phase = 'Bipedestación (De Pie)';
    return {
      index: idx + 1,
      hr: hr,
      phase: phase
    };
  }) || [];

  return (
    <div className="space-y-6">
      
      {/* Top Banner: Composite Fatigue Level */}
      <div className="rounded-2xl border border-slate-800 bg-[#0e131d] p-6 shadow-xl relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          
          {/* Left: Overall Diagnostic */}
          <div className="flex-1 space-y-3">
            <div className="flex flex-wrap items-center gap-2">
              <span className={`text-xs font-bold px-3 py-1 rounded-full border ${colorBadge} uppercase tracking-wider flex items-center gap-1.5`}>
                {current.overall_fatigue_score <= 55 ? <CheckCircle2 className="h-3.5 w-3.5" /> : <AlertTriangle className="h-3.5 w-3.5" />}
                {current.fatigue_state}
              </span>
              <span className="text-xs px-2.5 py-1 rounded bg-slate-800/80 text-slate-300 border border-slate-700">
                Estresor Principal: <strong className="text-cyan-400">{current.primary_stressor}</strong>
              </span>
            </div>

            <h2 className="text-2xl font-black text-white tracking-tight">
              Monitor Integral de Fatiga del Atleta
            </h2>
            <p className="text-xs text-slate-400 leading-relaxed max-w-3xl">
              Síntesis multivariable que combina la respuesta barorrefleja de la <strong>banda cardíaca pectoral</strong> (Test Ortostático), fatiga neuromuscular (asimetría biomecánica), deriva cardiovascular y temperatura basal nocturna.
            </p>

            <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs">
              <span className="text-slate-400 font-semibold block mb-1">Directriz del Preparador Físico:</span>
              <p className="text-slate-200 font-medium text-sm">
                "{current.recommendation}"
              </p>
            </div>
          </div>

          {/* Center: Fatigue Score Gauge */}
          <div className="flex flex-col items-center justify-center px-6 py-2 bg-slate-900/40 rounded-2xl border border-slate-800/60">
            <span className="text-xs uppercase font-bold text-slate-400 tracking-wider mb-1">
              Índice de Fatiga
            </span>
            <div className="flex items-baseline gap-1">
              <span className={`text-5xl font-black tracking-tight ${gaugeColor}`}>
                {current.overall_fatigue_score}
              </span>
              <span className="text-xs text-slate-400">/100</span>
            </div>
            <span className="text-[11px] text-slate-400 mt-1 font-medium">
              {current.overall_fatigue_score <= 30 ? 'Cuerpo Fresco / Regenerado' : current.overall_fatigue_score <= 55 ? 'Fatiga Adaptativa Normal' : 'Sobrecarga Requerida de Descarga'}
            </span>
          </div>

        </div>
      </div>

      {/* 4 Pillars Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        {/* Pillar 1: Autonomic (Chest Strap) */}
        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
              <Heart className="h-4 w-4 text-cyan-400" />
              Autonómico (40%)
            </span>
            <span className="text-xs font-black text-white">{current.pillars.autonomic} pts</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-2">
            <div
              className={`h-full ${current.pillars.autonomic > 65 ? 'bg-rose-400' : 'bg-cyan-400'}`}
              style={{ width: `${current.pillars.autonomic}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-300">
            <strong>Banda Polar H10 (ECG)</strong>: Test ortostático y respuesta barorrefleja postural.
          </p>
          <span className="text-[10px] text-slate-400 block mt-1">
            ΔHR: +{latestOrtho?.delta_hr || 0} bpm
          </span>
        </div>

        {/* Pillar 2: Cardiovascular (Decoupling) */}
        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-orange-400 flex items-center gap-1.5">
              <Flame className="h-4 w-4 text-orange-400" />
              Cardiovascular (25%)
            </span>
            <span className="text-xs font-black text-white">{current.pillars.cardiovascular} pts</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-2">
            <div
              className={`h-full ${current.pillars.cardiovascular > 65 ? 'bg-rose-400' : 'bg-orange-400'}`}
              style={{ width: `${current.pillars.cardiovascular}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-300">
            <strong>Potenciómetro + FC</strong>: Desacople aeróbico ($Pw:HR$) y ratio agudo/crónico.
          </p>
          <span className="text-[10px] text-slate-400 block mt-1">
            Deriva: {current.aerobic_decoupling_pct || 0}% ({current.aerobic_decoupling_pct && current.aerobic_decoupling_pct > 5 ? 'Elevada' : 'Controlada'})
          </span>
        </div>

        {/* Pillar 3: Neuromuscular (HRM-Pro Asymmetry) */}
        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <Footprints className="h-4 w-4 text-emerald-400" />
              Neuromuscular (20%)
            </span>
            <span className="text-xs font-black text-white">{current.pillars.neuromuscular} pts</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-2">
            <div
              className={`h-full ${current.pillars.neuromuscular > 65 ? 'bg-rose-400' : 'bg-emerald-400'}`}
              style={{ width: `${current.pillars.neuromuscular}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-300">
            <strong>Garmin HRM-Pro Plus</strong>: Asimetría de tiempo de contacto con el suelo (GCT).
          </p>
          <span className="text-[10px] text-slate-400 block mt-1">
            Asimetría: {current.gct_asymmetry_pct || 0}% ({current.gct_asymmetry_pct && current.gct_asymmetry_pct > 1.5 ? 'Fatiga Unilateral' : 'Simétrico'})
          </span>
        </div>

        {/* Pillar 4: Metabolic / Temp (Oura Ring) */}
        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
              <Thermometer className="h-4 w-4 text-indigo-400" />
              Metabólico / Temp (15%)
            </span>
            <span className="text-xs font-black text-white">{current.pillars.metabolic_temp} pts</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-2">
            <div
              className={`h-full ${current.pillars.metabolic_temp > 65 ? 'bg-rose-400' : 'bg-indigo-400'}`}
              style={{ width: `${current.pillars.metabolic_temp}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-300">
            <strong>Oura Ring Gen 3</strong>: Desviación de temperatura basal corporal nocturna.
          </p>
          <span className="text-[10px] text-slate-400 block mt-1">
            ΔT: {current.nocturnal_temp_deviation && current.nocturnal_temp_deviation > 0 ? `+${current.nocturnal_temp_deviation}` : current.nocturnal_temp_deviation}°C
          </span>
        </div>

      </div>

      {/* Main Focus: Orthostatic Test with Chest Strap */}
      <div className="p-6 rounded-2xl bg-[#0e131d] border border-slate-800 shadow-xl space-y-4">
        
        {/* Header & Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 text-xs font-bold border border-cyan-500/20">
                BANDA CARDÍACA PECTORAL ECG
              </span>
              <span className="text-xs text-slate-400">
                Dispositivo: <strong className="text-white">{latestOrtho?.device_name || 'Polar H10'}</strong>
              </span>
            </div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Activity className="h-5 w-5 text-cyan-400" />
              Test Ortostático Matutino (Barorreflejo Postural)
            </h3>
            <p className="text-xs text-slate-400">
              Evaluación del estado del sistema nervioso autónomo midiendo la transición Supino (acostado) a Bipedestación (de pie)
            </p>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={selectedDevice}
              onChange={(e) => setSelectedDevice(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-xs rounded-lg px-2.5 py-2 text-white focus:outline-none cursor-pointer"
            >
              <option value="Polar H10 (Banda ECG)">Polar H10 (Banda ECG)</option>
              <option value="Garmin HRM-Pro Plus">Garmin HRM-Pro Plus</option>
              <option value="Wahoo TICKR X">Wahoo TICKR X</option>
            </select>

            <button
              onClick={handleRunLiveTest}
              disabled={runningTest}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs transition shadow-lg shadow-cyan-500/20 disabled:opacity-50 cursor-pointer"
            >
              {runningTest ? (
                <>
                  <RotateCw className="h-4 w-4 animate-spin" />
                  Midiendo ECG...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 fill-current" />
                  Ejecutar Nuevo Test
                </>
              )}
            </button>
          </div>
        </div>

        {/* Test Success Feedback */}
        {testSuccessMessage && (
          <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-300 flex items-center gap-2 animate-fade-in">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
            <span>{testSuccessMessage}</span>
          </div>
        )}

        {/* Orthostatic Metrics Summary Cards */}
        {latestOrtho && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 block mb-0.5">FC Supino (Acostado)</span>
              <div className="flex items-baseline gap-1.5">
                <span className="text-xl font-bold text-white">{latestOrtho.supine_avg_hr}</span>
                <span className="text-[11px] text-slate-400">bpm</span>
              </div>
              <span className="text-[10px] text-cyan-400">RMSSD: {latestOrtho.supine_rmssd} ms</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 block mb-0.5">Pico Postural</span>
              <div className="flex items-baseline gap-1.5">
                <span className="text-xl font-bold text-amber-400">{latestOrtho.stand_peak_hr}</span>
                <span className="text-[11px] text-slate-400">bpm</span>
              </div>
              <span className="text-[10px] text-slate-400">Respuesta Barorrefleja</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 block mb-0.5">FC De Pie (Estabilizada)</span>
              <div className="flex items-baseline gap-1.5">
                <span className="text-xl font-bold text-white">{latestOrtho.stand_avg_hr}</span>
                <span className="text-[11px] text-slate-400">bpm</span>
              </div>
              <span className="text-[10px] text-indigo-400">RMSSD: {latestOrtho.stand_rmssd} ms</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 block mb-0.5">Diferencial Postural (ΔHR)</span>
              <div className="flex items-baseline gap-1.5">
                <span className="text-xl font-bold text-emerald-400">+{latestOrtho.delta_hr}</span>
                <span className="text-[11px] text-slate-400">bpm</span>
              </div>
              <span className="text-[10px] text-emerald-400 font-semibold">{latestOrtho.status_label}</span>
            </div>
          </div>
        )}

        {/* Orthostatic Transition Line Chart */}
        <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/80">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-3">
            <span>Curva de Frecuencia Cardíaca Segundo a Segundo (Transición Supino → De Pie):</span>
            <div className="flex items-center gap-4 text-[11px]">
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="h-2 w-2 rounded-full bg-cyan-400"></span>
                Fase Supino
              </span>
              <span className="flex items-center gap-1.5 text-amber-300">
                <span className="h-2 w-2 rounded-full bg-amber-400"></span>
                Pico Transición
              </span>
              <span className="flex items-center gap-1.5 text-indigo-300">
                <span className="h-2 w-2 rounded-full bg-indigo-400"></span>
                Bipedestación
              </span>
            </div>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={orthoChartData} margin={{ top: 10, right: 10, bottom: 0, left: -10 }}>
                <XAxis dataKey="index" stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 10 }} label={{ value: "Tiempo (segundos)", position: "insideBottom", offset: -2, fill: "#64748b", fontSize: 10 }} />
                <YAxis stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 10 }} domain={['dataMin - 5', 'dataMax + 8']} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#1e293b', borderRadius: '8px' }}
                  labelStyle={{ color: '#ffffff', fontWeight: 'bold' }}
                />
                
                {/* Reference line for standing baseline */}
                {latestOrtho && (
                  <ReferenceLine y={latestOrtho.stand_avg_hr} stroke="#818cf8" strokeDasharray="3 3" label={{ value: `De Pie: ${latestOrtho.stand_avg_hr} bpm`, fill: '#818cf8', fontSize: 10 }} />
                )}

                <Line
                  type="monotone"
                  dataKey="hr"
                  stroke="#00f2fe"
                  strokeWidth={2.5}
                  name="FC (bpm)"
                  dot={{ r: 2, fill: '#00f2fe' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Detailed Interpretation from sports science engine */}
          {latestOrtho && (
            <div className="mt-3 p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
              <strong className="text-white block mb-1">Diagnóstico Fisiológico:</strong>
              {latestOrtho.interpretation}
            </div>
          )}
        </div>

      </div>

    </div>
  );
};
