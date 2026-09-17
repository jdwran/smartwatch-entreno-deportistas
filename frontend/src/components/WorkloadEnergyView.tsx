import React from 'react';
import { WorkoutSession, WorkloadDay } from '../types';
import { Flame, Zap, Timer, Award, AlertOctagon, TrendingUp, Info } from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ReferenceArea,
  ReferenceLine
} from 'recharts';

interface WorkloadEnergyViewProps {
  workouts: WorkoutSession[];
  workloadHistory: WorkloadDay[];
}

export const WorkloadEnergyView: React.FC<WorkloadEnergyViewProps> = ({
  workouts,
  workloadHistory
}) => {
  const currentWorkload = workloadHistory[workloadHistory.length - 1];

  // Colors for HR zones
  const zoneColors = [
    '#38bdf8', // Z1 - light blue
    '#34d399', // Z2 - green
    '#facc15', // Z3 - yellow
    '#fb923c', // Z4 - orange
    '#f43f5e', // Z5 - red
  ];

  return (
    <div className="space-y-6">
      
      {/* Metrics Row: ACWR and Load Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Ratio ACWR Actual</span>
            <Flame className="h-4 w-4 text-orange-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">{currentWorkload?.acwr || 1.0}</span>
            <span className="text-xs text-slate-400">Aguda : Crónica</span>
          </div>
          <span className="text-xs text-emerald-400 font-medium">
            {currentWorkload?.zone_category || 'Óptimo (0.8 - 1.3)'}
          </span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Carga Aguda (7 Días)</span>
            <Zap className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">{currentWorkload?.acute_load || 0}</span>
            <span className="text-xs text-slate-400">TRIMP/día</span>
          </div>
          <span className="text-xs text-slate-400">Fatiga acumulada reciente</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Carga Crónica (28 Días)</span>
            <TrendingUp className="h-4 w-4 text-indigo-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">{currentWorkload?.chronic_load || 0}</span>
            <span className="text-xs text-slate-400">TRIMP/día</span>
          </div>
          <span className="text-xs text-indigo-400">Capacidad aeróbica / Fitness</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0e131d] border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-semibold uppercase">Gasto Total Semana</span>
            <Award className="h-4 w-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">
              {workouts.slice(0, 7).reduce((acc, w) => acc + w.calories_burned, 0).toLocaleString()}
            </span>
            <span className="text-xs text-slate-400">kcal activas</span>
          </div>
          <span className="text-xs text-slate-400">Fórmula de Keytel et al.</span>
        </div>
      </div>

      {/* Main ACWR & Workload Interactive Chart */}
      <div className="p-5 rounded-2xl bg-[#0e131d] border border-slate-800 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-cyan-400" />
              Modelo de Carga Aguda:Crónica (ACWR) - 30 Días
            </h3>
            <p className="text-xs text-slate-400">
              Control de sobrecarga y prevención de lesiones en deportistas de alto rendimiento
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1 text-emerald-400 font-semibold">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-400/30 border border-emerald-400"></span>
              Sweet Spot (0.8 - 1.3)
            </span>
            <span className="flex items-center gap-1 text-rose-400 font-semibold">
              <span className="h-2.5 w-2.5 rounded-full bg-rose-400/30 border border-rose-400"></span>
              Peligro (&gt; 1.5)
            </span>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={workloadHistory} margin={{ top: 10, right: 20, bottom: 0, left: -10 }}>
              <XAxis
                dataKey="date"
                stroke="#475569"
                tick={{ fill: '#94a3b8', fontSize: 10 }}
                tickFormatter={(d) => d.slice(5)}
              />
              <YAxis
                yAxisId="load"
                orientation="left"
                stroke="#475569"
                tick={{ fill: '#94a3b8', fontSize: 10 }}
                domain={[0, 'auto']}
              />
              <YAxis
                yAxisId="acwr"
                orientation="right"
                stroke="#fb923c"
                tick={{ fill: '#fb923c', fontSize: 10 }}
                domain={[0.4, 2.0]}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#090d16', borderColor: '#1e293b', borderRadius: '8px' }}
                labelStyle={{ color: '#ffffff', fontWeight: 'bold' }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />

              {/* Reference Sweet Spot Band on secondary ACWR axis */}
              <ReferenceLine yAxisId="acwr" y={0.8} stroke="#10b981" strokeDasharray="3 3" label={{ value: "0.8 Base", fill: "#10b981", fontSize: 9 }} />
              <ReferenceLine yAxisId="acwr" y={1.3} stroke="#10b981" strokeDasharray="3 3" label={{ value: "1.3 Óptimo", fill: "#10b981", fontSize: 9 }} />
              <ReferenceLine yAxisId="acwr" y={1.5} stroke="#f43f5e" strokeDasharray="3 3" label={{ value: "1.5 Peligro", fill: "#f43f5e", fontSize: 9 }} />

              {/* Daily TRIMP Bars */}
              <Bar yAxisId="load" dataKey="daily_trimp" fill="#334155" name="TRIMP Diario" radius={[4, 4, 0, 0]} opacity={0.6} />

              {/* Acute & Chronic Load Lines */}
              <Line yAxisId="load" type="monotone" dataKey="acute_load" stroke="#00f2fe" strokeWidth={2.5} name="Carga Aguda (7d)" dot={false} />
              <Line yAxisId="load" type="monotone" dataKey="chronic_load" stroke="#818cf8" strokeWidth={2} strokeDasharray="4 4" name="Carga Crónica (28d)" dot={false} />

              {/* ACWR Line */}
              <Line yAxisId="acwr" type="monotone" dataKey="acwr" stroke="#fb923c" strokeWidth={3} name="ACWR Ratio" dot={{ r: 2, fill: '#fb923c' }} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Workout Sessions List with Heart Rate Zones */}
      <div className="p-5 rounded-2xl bg-[#0e131d] border border-slate-800 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Zap className="h-5 w-5 text-amber-400" />
              Entrenamientos & Gasto Energético Fisiológico
            </h3>
            <p className="text-xs text-slate-400">
              Desglose de sesiones registradas con cálculo de TRIMP (Edwards & Banister) y zonas FC
            </p>
          </div>
          <span className="text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-300">
            {workouts.length} Sesiones Analizadas
          </span>
        </div>

        <div className="space-y-3">
          {workouts.map((w) => {
            const durationMin = Math.round(w.duration_seconds / 60);
            return (
              <div
                key={w.id}
                className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition"
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
                  <div className="flex items-center gap-3">
                    <span className="px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider bg-slate-800 text-cyan-400 border border-slate-700">
                      {w.sport_type}
                    </span>
                    <div>
                      <h4 className="text-sm font-bold text-white flex items-center gap-2">
                        {w.device_brand} {w.device_model || ''}
                        <span className="text-[10px] font-normal px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                          {w.source}
                        </span>
                      </h4>
                      <p className="text-xs text-slate-400">
                        {new Date(w.start_time).toLocaleDateString()} a las {new Date(w.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  </div>

                  {/* Summary Badges */}
                  <div className="flex flex-wrap items-center gap-3 text-xs">
                    <div className="flex items-center gap-1 text-slate-300">
                      <Timer className="h-3.5 w-3.5 text-slate-400" />
                      <span>{durationMin} min</span>
                    </div>
                    {w.distance_meters ? (
                      <div className="text-slate-300 font-medium">
                        {(w.distance_meters / 1000).toFixed(1)} km
                      </div>
                    ) : null}
                    <div className="text-slate-300">
                      FC Med: <strong className="text-white">{w.avg_hr}</strong> bpm (Máx: {w.max_hr})
                    </div>
                    <div className="px-2 py-0.5 rounded bg-orange-500/10 text-orange-400 font-bold border border-orange-500/20">
                      {w.calories_burned} kcal
                    </div>
                    <div className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-bold border border-cyan-500/20">
                      TRIMP: {w.trimp_edwards}
                    </div>
                  </div>
                </div>

                {/* Heart Rate Zones Bar */}
                {w.zones && w.zones.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
                      <span>Distribución de Zonas Fisiológicas de Frecuencia Cardíaca:</span>
                      <div className="flex gap-3">
                        {w.zones.map((z, idx) => (
                          <span key={z.zone} className="flex items-center gap-1">
                            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: zoneColors[idx] }}></span>
                            Z{z.zone}: {z.percentage}%
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="w-full h-2.5 rounded-full overflow-hidden flex bg-slate-800">
                      {w.zones.map((z, idx) => (
                        <div
                          key={z.zone}
                          style={{
                            width: `${z.percentage}%`,
                            backgroundColor: zoneColors[idx]
                          }}
                          title={`Z${z.zone} (${z.name}): ${z.percentage}% - ${Math.round(z.time_in_seconds / 60)} min`}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
};
