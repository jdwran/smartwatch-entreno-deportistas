import React, { useState } from 'react';
import { PhysiologicalAlert, AthleteProfile } from '../types';
import {
  AlertTriangle,
  Flame,
  Activity,
  Heart,
  Moon,
  ShieldAlert,
  CheckCircle2,
  Clock,
  Sparkles,
  RefreshCw,
  SlidersHorizontal,
  ChevronRight,
  Thermometer,
  Zap,
  Info
} from 'lucide-react';

interface AlertsCenterViewProps {
  alerts: PhysiologicalAlert[];
  athlete: AthleteProfile;
  onAcknowledge: (alertId: string) => Promise<void>;
  onSimulateAlert: (scenario: string) => Promise<void>;
  onRefresh: () => void;
  loading: boolean;
}

export const AlertsCenterView: React.FC<AlertsCenterViewProps> = ({
  alerts,
  athlete,
  onAcknowledge,
  onSimulateAlert,
  onRefresh,
  loading
}) => {
  const [severityFilter, setSeverityFilter] = useState<'ALL' | 'CRITICAL' | 'HIGH' | 'WARNING'>('ALL');
  const [onlyUnacknowledged, setOnlyUnacknowledged] = useState(false);
  const [simulatingScenario, setSimulatingScenario] = useState<string | null>(null);
  const [acknowledgingId, setAcknowledgingId] = useState<string | null>(null);

  // Filtered alerts
  const filteredAlerts = alerts.filter(a => {
    if (onlyUnacknowledged && a.acknowledged) return false;
    if (severityFilter !== 'ALL' && a.severity !== severityFilter) return false;
    return true;
  });

  const criticalCount = alerts.filter(a => a.severity === 'CRITICAL' && !a.acknowledged).length;
  const highCount = alerts.filter(a => a.severity === 'HIGH' && !a.acknowledged).length;
  const warningCount = alerts.filter(a => a.severity === 'WARNING' && !a.acknowledged).length;
  const totalUnack = alerts.filter(a => !a.acknowledged).length;

  const handleSimulate = async (scenario: string) => {
    try {
      setSimulatingScenario(scenario);
      await onSimulateAlert(scenario);
    } finally {
      setSimulatingScenario(null);
    }
  };

  const handleAcknowledge = async (id: string) => {
    try {
      setAcknowledgingId(id);
      await onAcknowledge(id);
    } finally {
      setAcknowledgingId(null);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'METABOLIC_TEMP':
        return <Thermometer className="h-4 w-4 text-rose-400" />;
      case 'NEUROMUSCULAR':
        return <Activity className="h-4 w-4 text-amber-400" />;
      case 'CARDIOVASCULAR':
        return <Flame className="h-4 w-4 text-orange-400" />;
      case 'AUTONOMIC':
        return <Heart className="h-4 w-4 text-violet-400" />;
      case 'SLEEP':
        return <Moon className="h-4 w-4 text-cyan-400" />;
      default:
        return <Info className="h-4 w-4 text-slate-400" />;
    }
  };

  const getSeverityBadge = (severity: string, acknowledged: boolean) => {
    if (acknowledged) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-800 text-slate-400 border border-slate-700">
          <CheckCircle2 className="h-3 w-3 text-emerald-400" />
          Revisada / Gestionada
        </span>
      );
    }

    switch (severity) {
      case 'CRITICAL':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-black bg-rose-500/20 text-rose-300 border border-rose-500/50 animate-pulse">
            <span className="h-1.5 w-1.5 rounded-full bg-rose-500 animate-ping"></span>
            CRÍTICA URGENTE
          </span>
        );
      case 'HIGH':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
            <AlertTriangle className="h-3 w-3 text-amber-400" />
            RIESGO ALTO
          </span>
        );
      case 'WARNING':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-yellow-500/20 text-yellow-300 border border-yellow-500/30">
            <ShieldAlert className="h-3 w-3 text-yellow-400" />
            ADVERTENCIA
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
            INFO
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Description */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-[#0d121f] to-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="h-2 w-2 rounded-full bg-rose-500 animate-ping" />
            <h2 className="text-lg md:text-xl font-black text-white tracking-wide">
              Centro de Triaje Fisiológico & Alertas Biométricas
            </h2>
          </div>
          <p className="text-xs md:text-sm text-slate-400 max-w-2xl">
            Vigilancia en tiempo real de biomarcadores alarmantes para <strong className="text-white">{athlete.name}</strong>. Detección proactiva de fiebre, asimetría lesiva, colapso vagal y sobrecarga aguda.
          </p>
        </div>

        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 hover:border-cyan-500 text-xs font-semibold text-slate-200 transition disabled:opacity-50 self-start md:self-auto cursor-pointer"
        >
          <RefreshCw className={`h-4 w-4 text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
          <span>Sincronizar Alertas</span>
        </button>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Sin Gestionar</span>
            <AlertTriangle className="h-4 w-4 text-rose-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl md:text-3xl font-black text-white">{totalUnack}</span>
            <span className="text-xs text-slate-500">de {alerts.length} totales</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/30">
          <div className="flex items-center justify-between">
            <span className="text-xs text-rose-400 font-semibold uppercase tracking-wider">Críticas Pendientes</span>
            <span className="h-2 w-2 rounded-full bg-rose-500 animate-ping" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl md:text-3xl font-black text-rose-400">{criticalCount}</span>
            <span className="text-xs text-rose-400/70">atención urgente</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30">
          <div className="flex items-center justify-between">
            <span className="text-xs text-amber-400 font-semibold uppercase tracking-wider">Alto Riesgo</span>
            <ShieldAlert className="h-4 w-4 text-amber-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl md:text-3xl font-black text-amber-400">{highCount}</span>
            <span className="text-xs text-amber-400/70">modificar carga</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-yellow-950/15 border border-yellow-500/25">
          <div className="flex items-center justify-between">
            <span className="text-xs text-yellow-400 font-semibold uppercase tracking-wider">Advertencias</span>
            <Info className="h-4 w-4 text-yellow-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl md:text-3xl font-black text-yellow-400">{warningCount}</span>
            <span className="text-xs text-yellow-400/70">monitoreo continuo</span>
          </div>
        </div>
      </div>

      {/* Live Simulation Trigger Bar */}
      <div className="p-4 md:p-5 rounded-2xl bg-[#0b0f19] border border-cyan-500/20 shadow-lg">
        <div className="flex items-center justify-between gap-3 mb-3 flex-wrap">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-cyan-400" />
            <h3 className="text-xs md:text-sm font-bold text-white uppercase tracking-wider">
              Simulador de Telemetría Biológica Alarmante (Live Injector)
            </h3>
          </div>
          <span className="text-[11px] text-slate-400">
            Haz clic para inyectar una anomalía fisiológica real y verificar el protocolo de triaje
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
          <button
            onClick={() => handleSimulate('fever')}
            disabled={simulatingScenario !== null}
            className="flex items-center justify-between p-2.5 rounded-xl bg-rose-950/30 hover:bg-rose-900/50 border border-rose-500/30 text-left transition group disabled:opacity-50 cursor-pointer"
          >
            <div>
              <div className="text-xs font-bold text-rose-300 flex items-center gap-1.5">
                <Thermometer className="h-3.5 w-3.5 text-rose-400" />
                <span>Fiebre (+0.65°C)</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">Oura Ring NTC</p>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-rose-400 group-hover:translate-x-0.5 transition" />
          </button>

          <button
            onClick={() => handleSimulate('gct_asymmetry')}
            disabled={simulatingScenario !== null}
            className="flex items-center justify-between p-2.5 rounded-xl bg-rose-950/30 hover:bg-rose-900/50 border border-rose-500/30 text-left transition group disabled:opacity-50 cursor-pointer"
          >
            <div>
              <div className="text-xs font-bold text-rose-300 flex items-center gap-1.5">
                <Activity className="h-3.5 w-3.5 text-rose-400" />
                <span>Asimetría GCT (3.2%)</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">Garmin HRM-Pro</p>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-rose-400 group-hover:translate-x-0.5 transition" />
          </button>

          <button
            onClick={() => handleSimulate('acwr_danger')}
            disabled={simulatingScenario !== null}
            className="flex items-center justify-between p-2.5 rounded-xl bg-rose-950/30 hover:bg-rose-900/50 border border-rose-500/30 text-left transition group disabled:opacity-50 cursor-pointer"
          >
            <div>
              <div className="text-xs font-bold text-rose-300 flex items-center gap-1.5">
                <Flame className="h-3.5 w-3.5 text-rose-400" />
                <span>Carga ACWR (1.68)</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">APEX TRIMP Engine</p>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-rose-400 group-hover:translate-x-0.5 transition" />
          </button>

          <button
            onClick={() => handleSimulate('baroreflex_failure')}
            disabled={simulatingScenario !== null}
            className="flex items-center justify-between p-2.5 rounded-xl bg-rose-950/30 hover:bg-rose-900/50 border border-rose-500/30 text-left transition group disabled:opacity-50 cursor-pointer"
          >
            <div>
              <div className="text-xs font-bold text-rose-300 flex items-center gap-1.5">
                <Heart className="h-3.5 w-3.5 text-rose-400" />
                <span>Falla Barorrefleja</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">Polar H10 ECG</p>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-rose-400 group-hover:translate-x-0.5 transition" />
          </button>

          <button
            onClick={() => handleSimulate('rmssd_collapse')}
            disabled={simulatingScenario !== null}
            className="flex items-center justify-between p-2.5 rounded-xl bg-amber-950/30 hover:bg-amber-900/50 border border-amber-500/30 text-left transition group disabled:opacity-50 cursor-pointer"
          >
            <div>
              <div className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                <Heart className="h-3.5 w-3.5 text-amber-400" />
                <span>Colapso RMSSD (-48%)</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">Whoop 4.0 / Apple</p>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-amber-400 group-hover:translate-x-0.5 transition" />
          </button>

          <button
            onClick={() => handleSimulate('aerobic_drift')}
            disabled={simulatingScenario !== null}
            className="flex items-center justify-between p-2.5 rounded-xl bg-amber-950/30 hover:bg-amber-900/50 border border-amber-500/30 text-left transition group disabled:opacity-50 cursor-pointer"
          >
            <div>
              <div className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                <Zap className="h-3.5 w-3.5 text-amber-400" />
                <span>Deriva Pw:HR (+8.9%)</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">Stryd / Favero Assioma</p>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-amber-400 group-hover:translate-x-0.5 transition" />
          </button>

          <button
            onClick={() => handleSimulate('tachycardia_ortho')}
            disabled={simulatingScenario !== null}
            className="flex items-center justify-between p-2.5 rounded-xl bg-amber-950/30 hover:bg-amber-900/50 border border-amber-500/30 text-left transition group disabled:opacity-50 cursor-pointer"
          >
            <div>
              <div className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                <Activity className="h-3.5 w-3.5 text-amber-400" />
                <span>Taquicardia (+34 bpm)</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">Test Ortostático ECG</p>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-amber-400 group-hover:translate-x-0.5 transition" />
          </button>

          <button
            onClick={() => handleSimulate('non_dipper')}
            disabled={simulatingScenario !== null}
            className="flex items-center justify-between p-2.5 rounded-xl bg-yellow-950/25 hover:bg-yellow-900/40 border border-yellow-500/30 text-left transition group disabled:opacity-50 cursor-pointer"
          >
            <div>
              <div className="text-xs font-bold text-yellow-300 flex items-center gap-1.5">
                <Moon className="h-3.5 w-3.5 text-yellow-400" />
                <span>Sueño Non-Dipper</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">Apple Watch Ultra</p>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-yellow-400 group-hover:translate-x-0.5 transition" />
          </button>
        </div>
      </div>

      {/* Filter and Triage Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-900/90 border border-slate-800">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-slate-400 flex items-center gap-1 mr-1">
            <SlidersHorizontal className="h-3.5 w-3.5" />
            Severidad:
          </span>

          <button
            onClick={() => setSeverityFilter('ALL')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition cursor-pointer ${
              severityFilter === 'ALL'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                : 'text-slate-400 hover:text-white bg-slate-800/60'
            }`}
          >
            Todas ({alerts.length})
          </button>

          <button
            onClick={() => setSeverityFilter('CRITICAL')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition cursor-pointer ${
              severityFilter === 'CRITICAL'
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/50'
                : 'text-slate-400 hover:text-rose-300 bg-slate-800/60'
            }`}
          >
            Críticas ({alerts.filter(a => a.severity === 'CRITICAL').length})
          </button>

          <button
            onClick={() => setSeverityFilter('HIGH')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition cursor-pointer ${
              severityFilter === 'HIGH'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50'
                : 'text-slate-400 hover:text-amber-300 bg-slate-800/60'
            }`}
          >
            Altas ({alerts.filter(a => a.severity === 'HIGH').length})
          </button>

          <button
            onClick={() => setSeverityFilter('WARNING')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition cursor-pointer ${
              severityFilter === 'WARNING'
                ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/40'
                : 'text-slate-400 hover:text-yellow-300 bg-slate-800/60'
            }`}
          >
            Advertencias ({alerts.filter(a => a.severity === 'WARNING').length})
          </button>
        </div>

        <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={onlyUnacknowledged}
            onChange={(e) => setOnlyUnacknowledged(e.target.checked)}
            className="rounded border-slate-700 bg-slate-800 text-cyan-500 focus:ring-0 cursor-pointer"
          />
          <span>Mostrar solo no gestionadas ({totalUnack})</span>
        </label>
      </div>

      {/* Alerts Cards List */}
      <div className="space-y-3.5">
        {filteredAlerts.length === 0 ? (
          <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800 text-slate-400">
            <CheckCircle2 className="h-10 w-10 text-emerald-400 mx-auto mb-3" />
            <h4 className="text-base font-bold text-white">No hay alertas con estos filtros</h4>
            <p className="text-xs text-slate-400 mt-1">
              Todos los biomarcadores del deportista se encuentran en parámetros fisiológicos seguros.
            </p>
          </div>
        ) : (
          filteredAlerts.map(alert => {
            const isCritical = alert.severity === 'CRITICAL';
            const isHigh = alert.severity === 'HIGH';

            return (
              <div
                key={alert.id}
                className={`p-5 rounded-2xl border transition-all ${
                  alert.acknowledged
                    ? 'bg-slate-900/40 border-slate-800/80 opacity-70 hover:opacity-100'
                    : isCritical
                    ? 'bg-[#150a0f] border-rose-500/40 shadow-lg shadow-rose-950/20'
                    : isHigh
                    ? 'bg-[#150f0a] border-amber-500/40'
                    : 'bg-slate-900/80 border-slate-800'
                }`}
              >
                <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                  {/* Left info */}
                  <div className="space-y-2.5 flex-1">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      {getSeverityBadge(alert.severity, alert.acknowledged)}

                      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                        {getCategoryIcon(alert.category)}
                        {alert.category}
                      </span>

                      <span className="text-xs text-slate-400 font-mono bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/60">
                        {alert.device_source}
                      </span>

                      <span className="text-[11px] text-slate-500 flex items-center gap-1 ml-auto lg:ml-0">
                        <Clock className="h-3 w-3" />
                        {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {alert.date}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      {alert.title}
                    </h3>

                    <p className="text-xs text-slate-300 leading-relaxed">
                      {alert.description}
                    </p>

                    {/* Metric trigger detail */}
                    <div className="flex flex-wrap items-center gap-3 p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs">
                      <span className="text-slate-400">
                        Métrica Disparadora: <strong className="text-white font-mono">{alert.trigger_metric}</strong>
                      </span>
                      <span className="text-slate-500">|</span>
                      <span className="text-slate-400">
                        Valor Registrado: <strong className={isCritical ? 'text-rose-400 font-mono' : isHigh ? 'text-amber-400 font-mono' : 'text-yellow-400 font-mono'}>{alert.trigger_value}</strong>
                      </span>
                      <span className="text-slate-500">|</span>
                      <span className="text-slate-400">
                        Umbral Crítico: <span className="text-slate-300 font-mono">{alert.threshold}</span>
                      </span>
                    </div>

                    {/* Action required protocol */}
                    <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs">
                      <span className="font-bold text-rose-300 block mb-0.5">
                        ⚠️ Protocolo de Intervención / Acción Requerida:
                      </span>
                      <span className="text-slate-200">
                        {alert.action_required}
                      </span>
                    </div>
                  </div>

                  {/* Right: Acknowledge button */}
                  <div className="flex-shrink-0 flex items-center lg:flex-col gap-2 justify-end">
                    {alert.acknowledged ? (
                      <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold">
                        <CheckCircle2 className="h-4 w-4" />
                        <span>Gestionada por Staff</span>
                      </div>
                    ) : (
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        disabled={acknowledgingId === alert.id}
                        className={`flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-bold transition shadow-md cursor-pointer ${
                          isCritical
                            ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/30'
                            : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-emerald-500/50'
                        }`}
                      >
                        <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                        <span>{acknowledgingId === alert.id ? 'Gestionando...' : 'Gestionar / Marcar Revisada'}</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
