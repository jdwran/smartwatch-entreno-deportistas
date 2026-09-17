import React from 'react';
import { HRVReading, DailyReadiness } from '../types';
import { Heart, Activity, ShieldAlert, Sparkles, HelpCircle } from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ReferenceArea
} from 'recharts';

interface HRVDeepDiveProps {
  hrvReadings: HRVReading[];
  currentReadiness: DailyReadiness | null;
}

export const HRVDeepDive: React.FC<HRVDeepDiveProps> = ({
  hrvReadings,
  currentReadiness
}) => {
  const latestHRV = hrvReadings[hrvReadings.length - 1];

  const chartData = hrvReadings.map(r => ({
    date: r.timestamp.slice(5, 10),
    rmssd: r.rmssd,
    baseline: r.baseline_7d_mean,
    swc_lower: r.swc_lower,
    swc_upper: r.swc_upper,
    status: r.status
  }));

  return (
    <div className="space-y-6">
      
      {/* Top Banner with Latest HRV Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">RMSSD Actual (rMSSD)</span>
            <Heart className="h-4 w-4 text-rose-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">{latestHRV?.rmssd || 0}</span>
            <span className="text-xs text-slate-400">milisegundos</span>
          </div>
          <span className="text-xs text-cyan-400 font-medium">
            ln(RMSSD): {latestHRV?.ln_rmssd || 0}
          </span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Línea Base Móvil 7D</span>
            <Activity className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">{latestHRV?.baseline_7d_mean || 0}</span>
            <span className="text-xs text-slate-400">ms ± {latestHRV?.baseline_7d_sd || 0}</span>
          </div>
          <span className="text-xs text-slate-400">
            Corredor SWC: [{latestHRV?.swc_lower} - {latestHRV?.swc_upper}] ms
          </span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Sensor de Origen</span>
            <Sparkles className="h-4 w-4 text-amber-400" />
          </div>
          <div className="text-lg font-bold text-white mt-1">
            {latestHRV?.source_device || 'Banda Pectoral ECG'}
          </div>
          <span className="text-xs text-emerald-400 font-medium">
            Precisión Milisegundo a Milisegundo (R-R)
          </span>
        </div>

      </div>

      {/* HRV Baseline Chart with SWC Tunnel */}
      <div className="p-5 rounded-2xl bg-[#0e131d] border border-slate-800 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Heart className="h-5 w-5 text-rose-400" />
              Tendencia de HRV con Banda de Cambio Mínimo Relevante (SWC)
            </h3>
            <p className="text-xs text-slate-400">
              Método estándar en fisiología deportiva para detectar fatiga del Sistema Nervioso Autónomo
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1 text-cyan-400">
              <span className="h-2 w-2 rounded-full bg-cyan-400"></span>
              RMSSD Diario
            </span>
            <span className="flex items-center gap-1 text-indigo-400">
              <span className="h-2 w-2 rounded-full bg-indigo-400"></span>
              Media Móvil 7d
            </span>
            <span className="flex items-center gap-1 text-slate-400">
              <span className="h-2 w-2 rounded bg-slate-700"></span>
              Corredor SWC (±0.5 SD)
            </span>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 10, bottom: 0, left: -10 }}>
              <XAxis dataKey="date" stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 10 }} />
              <YAxis stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 10 }} domain={['dataMin - 10', 'dataMax + 10']} />
              <Tooltip
                contentStyle={{ backgroundColor: '#090d16', borderColor: '#1e293b', borderRadius: '8px' }}
                labelStyle={{ color: '#ffffff', fontWeight: 'bold' }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />

              {/* Upper & Lower SWC Bounds creating the safety corridor */}
              <Line type="monotone" dataKey="swc_upper" stroke="#334155" strokeDasharray="2 2" name="Límite Superior SWC" dot={false} />
              <Line type="monotone" dataKey="swc_lower" stroke="#334155" strokeDasharray="2 2" name="Límite Inferior SWC" dot={false} />

              {/* 7-day Rolling Baseline Mean */}
              <Line type="monotone" dataKey="baseline" stroke="#818cf8" strokeWidth={2} name="Línea Base 7d" dot={false} />

              {/* Daily RMSSD */}
              <Line
                type="monotone"
                dataKey="rmssd"
                stroke="#00f2fe"
                strokeWidth={3}
                name="RMSSD Diario (ms)"
                dot={{ r: 4, fill: '#00f2fe', strokeWidth: 2, stroke: '#080b11' }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* HRV Scientific Interpretation Guide */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/50 border border-emerald-500/20">
          <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 mb-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
            LÍNEA BASE ÓPTIMA
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            El RMSSD se encuentra dentro del corredor SWC. Indica un tono parasimpático saludable y capacidad completa para asimilar sesiones intensas o de umbral (Z4/Z5).
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/50 border border-rose-500/20">
          <div className="flex items-center gap-2 text-xs font-bold text-rose-400 mb-2">
            <span className="h-2 w-2 rounded-full bg-rose-400"></span>
            FATIGA SIMPÁTICA
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            RMSSD por debajo del límite inferior con frecuencia cardíaca de reposo elevada. Respuesta clásica a sobrecarga aguda, privación de sueño o estrés neuroendocrino.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/50 border border-amber-500/20">
          <div className="flex items-center gap-2 text-xs font-bold text-amber-400 mb-2">
            <span className="h-2 w-2 rounded-full bg-amber-400"></span>
            SATURACIÓN PARASIMPÁTICA
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            RMSSD anormalmente alto acompañado de bradicardia pronunciada. Puede ser signo de fatiga acumulada profunda donde el sistema parasimpático hipercompensa.
          </p>
        </div>
      </div>

    </div>
  );
};
