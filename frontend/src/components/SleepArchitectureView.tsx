import React from 'react';
import { SleepRecord } from '../types';
import { Moon, BedDouble, ShieldCheck, HeartPulse, Sparkles, Clock, AlertCircle } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend
} from 'recharts';

interface SleepArchitectureViewProps {
  sleepData: {
    current: SleepRecord | null;
    history: SleepRecord[];
    averages: {
      efficiency: number;
      deep_minutes: number;
      rem_minutes: number;
      score: number;
    };
  } | null;
}

export const SleepArchitectureView: React.FC<SleepArchitectureViewProps> = ({
  sleepData
}) => {
  if (!sleepData || !sleepData.current) return null;

  const current = sleepData.current;
  const deepHours = (current.deep_sleep_minutes / 60).toFixed(1);
  const remHours = (current.rem_sleep_minutes / 60).toFixed(1);
  const totalHours = (current.total_sleep_minutes / 60).toFixed(1);
  const restorativePct = Math.round(((current.deep_sleep_minutes + current.rem_sleep_minutes) / current.total_sleep_minutes) * 100);

  const historyChartData = sleepData.history.map(s => ({
    date: s.date.slice(5),
    deep: Math.round(s.deep_sleep_minutes / 60 * 10) / 10,
    rem: Math.round(s.rem_sleep_minutes / 60 * 10) / 10,
    light: Math.round(s.light_sleep_minutes / 60 * 10) / 10,
    awake: Math.round(s.awake_minutes / 60 * 10) / 10,
    score: s.sleep_score
  }));

  return (
    <div className="space-y-6">
      
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Puntuación de Sueño</span>
            <Moon className="h-4 w-4 text-indigo-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">{current.sleep_score}</span>
            <span className="text-xs text-slate-400">/100</span>
          </div>
          <span className="text-xs text-emerald-400 font-medium">
            Eficiencia del {current.efficiency_percentage}%
          </span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Tiempo Total de Sueño</span>
            <Clock className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">{totalHours}</span>
            <span className="text-xs text-slate-400">horas</span>
          </div>
          <span className="text-xs text-slate-400">
            En cama: {(current.time_in_bed_minutes / 60).toFixed(1)} h
          </span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Sueño Restaurador</span>
            <Sparkles className="h-4 w-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">{restorativePct}%</span>
            <span className="text-xs text-slate-400">Profundo + REM</span>
          </div>
          <span className="text-xs text-amber-400 font-medium">
            Meta de Élite: &gt;40%
          </span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Caída Cardíaca (Dipping)</span>
            <HeartPulse className="h-4 w-4 text-rose-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">{current.hr_dip_percentage}%</span>
            <span className="text-xs text-slate-400">descenso nocturno</span>
          </div>
          <span className="text-xs text-emerald-400 font-medium">
            FC Nocturna: {current.nocturnal_rhr} bpm
          </span>
        </div>

      </div>

      {/* Sleep Stages Architecture Breakdown */}
      <div className="p-5 rounded-2xl bg-[#0e131d] border border-slate-800 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <BedDouble className="h-5 w-5 text-indigo-400" />
              Arquitectura del Sueño de la Última Noche
            </h3>
            <p className="text-xs text-slate-400">
              Registrado mediante {current.source_device}
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="px-2.5 py-1 rounded bg-slate-800 text-slate-300">
              FC Reposo Día: <strong>{current.daytime_rhr_baseline} bpm</strong>
            </span>
            <span className="px-2.5 py-1 rounded bg-slate-800 text-slate-300">
              FC Mínima Noche: <strong>{current.nocturnal_rhr} bpm</strong>
            </span>
          </div>
        </div>

        {/* Proportional Stage Bar */}
        <div className="w-full h-8 rounded-xl overflow-hidden flex bg-slate-800 mb-4 p-1 gap-1">
          <div
            style={{ width: `${(current.deep_sleep_minutes / current.total_sleep_minutes) * 100}%` }}
            className="bg-indigo-600 rounded-lg flex items-center justify-center text-[10px] font-bold text-white shadow"
            title={`Profundo: ${current.deep_sleep_minutes} min`}
          >
            Profundo {deepHours}h
          </div>
          <div
            style={{ width: `${(current.rem_sleep_minutes / current.total_sleep_minutes) * 100}%` }}
            className="bg-cyan-500 rounded-lg flex items-center justify-center text-[10px] font-bold text-black shadow"
            title={`REM: ${current.rem_sleep_minutes} min`}
          >
            REM {remHours}h
          </div>
          <div
            style={{ width: `${(current.light_sleep_minutes / current.total_sleep_minutes) * 100}%` }}
            className="bg-slate-600 rounded-lg flex items-center justify-center text-[10px] font-bold text-slate-200 shadow"
            title={`Ligero: ${current.light_sleep_minutes} min`}
          >
            Ligero {(current.light_sleep_minutes / 60).toFixed(1)}h
          </div>
          <div
            style={{ width: `${Math.max(4, (current.awake_minutes / current.total_sleep_minutes) * 100)}%` }}
            className="bg-rose-500/60 rounded-lg flex items-center justify-center text-[10px] font-bold text-white shadow"
            title={`Despierto: ${current.awake_minutes} min`}
          >
            {current.awake_minutes}m
          </div>
        </div>

        {/* Detailed Stage Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div className="p-3 rounded-xl bg-slate-900/60 border border-indigo-500/30">
            <div className="text-xs font-bold text-indigo-400 mb-1">Sueño Profundo (SWS)</div>
            <div className="text-xl font-extrabold text-white">{current.deep_sleep_minutes} min</div>
            <p className="text-[11px] text-slate-400 mt-1">
              Reparación muscular, liberación de GH y recuperación celular.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-cyan-500/30">
            <div className="text-xs font-bold text-cyan-400 mb-1">Sueño REM</div>
            <div className="text-xl font-extrabold text-white">{current.rem_sleep_minutes} min</div>
            <p className="text-[11px] text-slate-400 mt-1">
              Consolidación motora, memoria procedimental y reflejos neuromusculares.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-700/50">
            <div className="text-xs font-bold text-slate-300 mb-1">Sueño Ligero</div>
            <div className="text-xl font-extrabold text-white">{current.light_sleep_minutes} min</div>
            <p className="text-[11px] text-slate-400 mt-1">
              Transición fisiológica y mantenimiento de la homeostasis.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-rose-500/30">
            <div className="text-xs font-bold text-rose-400 mb-1">Despertares</div>
            <div className="text-xl font-extrabold text-white">{current.awake_minutes} min</div>
            <p className="text-[11px] text-slate-400 mt-1">
              Micro-interrupciones del descanso nocturno.
            </p>
          </div>
        </div>
      </div>

      {/* 14-Day Sleep Stage Trend */}
      <div className="p-5 rounded-2xl bg-[#0e131d] border border-slate-800 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Moon className="h-5 w-5 text-indigo-400" />
              Historial de Arquitectura de Sueño (Horas por Fase)
            </h3>
            <p className="text-xs text-slate-400">
              Tendencia multidiaria para monitorizar consistencia y deuda de sueño
            </p>
          </div>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={historyChartData} margin={{ top: 10, right: 10, bottom: 0, left: -10 }}>
              <XAxis dataKey="date" stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 10 }} />
              <YAxis stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 10 }} label={{ value: 'Horas', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }} />
              <Tooltip contentStyle={{ backgroundColor: '#090d16', borderColor: '#1e293b', borderRadius: '8px' }} />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              
              <Bar dataKey="deep" stackId="a" fill="#6366f1" name="Profundo (h)" />
              <Bar dataKey="rem" stackId="a" fill="#06b6d4" name="REM (h)" />
              <Bar dataKey="light" stackId="a" fill="#334155" name="Ligero (h)" />
              <Bar dataKey="awake" stackId="a" fill="#f43f5e" name="Despierto (h)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
};
