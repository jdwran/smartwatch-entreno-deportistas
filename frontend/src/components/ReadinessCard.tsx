import React from 'react';
import { DailyReadiness, AthleteProfile, HRVReading } from '../types';
import { Heart, Activity, Moon, BatteryCharging, AlertTriangle, CheckCircle2, Flame } from 'lucide-react';

interface ReadinessCardProps {
  athlete: AthleteProfile;
  readiness: DailyReadiness | null;
  hrvLatest?: HRVReading;
}

export const ReadinessCard: React.FC<ReadinessCardProps> = ({
  athlete,
  readiness,
  hrvLatest
}) => {
  if (!readiness) return null;

  const score = readiness.readiness_score;

  let colorClass = 'text-emerald-400 stroke-emerald-400';
  let bgGlow = 'from-emerald-500/10 via-emerald-500/5 to-transparent';
  let badgeClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  let statusText = 'Preparación Óptima';

  if (score < 60) {
    colorClass = 'text-rose-400 stroke-rose-400';
    bgGlow = 'from-rose-500/10 via-rose-500/5 to-transparent';
    badgeClass = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    statusText = 'Fatiga Severa / Recuperación Requerida';
  } else if (score < 75) {
    colorClass = 'text-amber-400 stroke-amber-400';
    bgGlow = 'from-amber-500/10 via-amber-500/5 to-transparent';
    badgeClass = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    statusText = 'Recuperación Moderada';
  }

  // Circular gauge math
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className={`relative overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-br ${bgGlow} bg-[#0e131d] p-6 shadow-xl`}>
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        
        {/* Left: Athlete Summary & Recommendation */}
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className={`text-xs font-bold px-2.5 py-1 rounded-full border ${badgeClass} uppercase tracking-wide flex items-center gap-1.5`}>
              {score >= 75 ? <CheckCircle2 className="h-3.5 w-3.5" /> : <AlertTriangle className="h-3.5 w-3.5" />}
              {statusText}
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              VO2max: <strong className="text-cyan-400">{athlete.vo2max} ml/kg/min</strong>
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              FC Reposo: <strong className="text-slate-100">{athlete.resting_hr} bpm</strong>
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              FC Máx: <strong className="text-slate-100">{athlete.max_hr} bpm</strong>
            </span>
          </div>

          <h2 className="text-2xl font-black text-white tracking-tight mt-1">
            {athlete.name}
          </h2>
          <p className="text-xs text-slate-400 mb-4">{athlete.sport}</p>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center gap-2 text-xs font-semibold text-cyan-400 mb-1">
              <Activity className="h-4 w-4" />
              Prescripción Diaria de Carga:
            </div>
            <p className="text-sm text-slate-200 leading-relaxed font-medium">
              "{readiness.training_recommendation}"
            </p>
            <div className="mt-2 flex items-center gap-2 text-xs">
              <span className="text-slate-400">Objetivo del Día:</span>
              <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/30">
                {readiness.intensity_target}
              </span>
            </div>
          </div>
        </div>

        {/* Center: Circular Readiness Gauge */}
        <div className="flex flex-col items-center justify-center px-4">
          <div className="relative w-36 h-36 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 128 128">
              {/* Background circle */}
              <circle
                cx="64"
                cy="64"
                r={radius}
                className="stroke-slate-800"
                strokeWidth="10"
                fill="none"
              />
              {/* Progress circle */}
              <circle
                cx="64"
                cy="64"
                r={radius}
                className={`${colorClass} transition-all duration-1000 ease-out`}
                strokeWidth="10"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="none"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center">
              <span className="text-3xl font-black text-white tracking-tight">
                {score}
              </span>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                Readiness
              </span>
            </div>
          </div>
          <span className="text-xs text-slate-400 mt-2 font-medium">
            Índice de Disposición Fisiológica
          </span>
        </div>

        {/* Right: Key Contributing Pillars */}
        <div className="w-full lg:w-72 grid grid-cols-2 gap-2.5">
          {/* HRV RMSSD */}
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-[11px] font-medium">HRV RMSSD</span>
              <Heart className="h-3.5 w-3.5 text-rose-400" />
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-xl font-bold text-white">{readiness.hrv_rmssd}</span>
              <span className="text-[11px] text-slate-400">ms</span>
            </div>
            <span className="text-[10px] text-cyan-400 font-medium">
              lnRMSSD: {readiness.hrv_ln_rmssd}
            </span>
          </div>

          {/* Sleep Score */}
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-[11px] font-medium">Calidad Sueño</span>
              <Moon className="h-3.5 w-3.5 text-indigo-400" />
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-xl font-bold text-white">{readiness.sleep_score}</span>
              <span className="text-[11px] text-slate-400">/100</span>
            </div>
            <span className="text-[10px] text-indigo-400 font-medium">
              Restaurador
            </span>
          </div>

          {/* ACWR Ratio */}
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-[11px] font-medium">ACWR (7:28d)</span>
              <Flame className="h-3.5 w-3.5 text-orange-400" />
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-xl font-bold text-white">{readiness.acwr}</span>
              <span className="text-[11px] text-slate-400">ratio</span>
            </div>
            <span className={`text-[10px] font-medium ${readiness.acwr <= 1.3 ? 'text-emerald-400' : 'text-amber-400'}`}>
              {readiness.acwr <= 1.3 ? 'Zona Óptima' : 'Vigilar Carga'}
            </span>
          </div>

          {/* Battery / Status */}
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-[11px] font-medium">SNC / Tono</span>
              <BatteryCharging className="h-3.5 w-3.5 text-cyan-400" />
            </div>
            <div className="text-sm font-bold text-white capitalize truncate">
              {readiness.hrv_status.replace('_', ' ')}
            </div>
            <span className="text-[10px] text-slate-400 font-medium">
              Equilibrio Vagal
            </span>
          </div>
        </div>

      </div>
    </div>
  );
};
