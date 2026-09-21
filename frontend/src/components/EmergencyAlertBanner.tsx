import React from 'react';
import { PhysiologicalAlert } from '../types';
import { AlertTriangle, BellRing, ShieldAlert, CheckCircle2, ArrowRight } from 'lucide-react';

interface EmergencyAlertBannerProps {
  alerts: PhysiologicalAlert[];
  onOpenAlertsCenter: () => void;
  onAcknowledge: (alertId: string) => void;
}

export const EmergencyAlertBanner: React.FC<EmergencyAlertBannerProps> = ({
  alerts,
  onOpenAlertsCenter,
  onAcknowledge
}) => {
  // Only show for unacknowledged critical or high alerts
  const urgentAlerts = alerts.filter(a => !a.acknowledged && (a.severity === 'CRITICAL' || a.severity === 'HIGH'));

  if (urgentAlerts.length === 0) return null;

  const topAlert = urgentAlerts[0];
  const isCritical = topAlert.severity === 'CRITICAL';

  return (
    <div className={`relative overflow-hidden rounded-2xl border p-4 shadow-xl transition-all duration-300 ${
      isCritical 
        ? 'bg-rose-950/40 border-rose-500/50 shadow-rose-950/30' 
        : 'bg-amber-950/40 border-amber-500/50 shadow-amber-950/30'
    }`}>
      {/* Background glow pulse */}
      <div className={`absolute -right-12 -top-12 h-36 w-36 rounded-full blur-3xl opacity-20 pointer-events-none ${
        isCritical ? 'bg-rose-500' : 'bg-amber-500'
      }`} />

      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Left: Icon & Description */}
        <div className="flex items-start gap-3.5">
          <div className={`p-2.5 rounded-xl border flex-shrink-0 mt-0.5 ${
            isCritical
              ? 'bg-rose-500/20 text-rose-400 border-rose-500/30 animate-pulse'
              : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
          }`}>
            <AlertTriangle className="h-6 w-6" />
          </div>

          <div>
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className={`px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-wider ${
                isCritical ? 'bg-rose-500 text-white' : 'bg-amber-500 text-slate-900'
              }`}>
                {isCritical ? 'EMERGENCIA FISIOLÓGICA CRÍTICA' : 'ALERTA DE ALTO RIESGO'}
              </span>

              <span className="text-xs font-mono text-slate-400 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-700/60">
                {topAlert.device_source}
              </span>

              {urgentAlerts.length > 1 && (
                <span className="text-xs font-bold text-rose-300 bg-rose-500/20 px-2 py-0.5 rounded-full border border-rose-500/40">
                  +{urgentAlerts.length - 1} alertas adicionales
                </span>
              )}
            </div>

            <h4 className="text-sm md:text-base font-bold text-white flex items-center gap-2">
              {topAlert.title}
            </h4>

            <p className="text-xs text-slate-300 mt-1 line-clamp-2 max-w-3xl">
              {topAlert.description}
            </p>

            <div className="flex items-center gap-3 mt-2 text-xs">
              <span className="text-slate-400">
                Métrica: <strong className="text-white font-mono">{topAlert.trigger_metric}</strong> = <strong className="text-rose-400 font-mono">{topAlert.trigger_value}</strong> (Límite: {topAlert.threshold})
              </span>
            </div>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2.5 w-full md:w-auto justify-end flex-wrap">
          <button
            onClick={() => onAcknowledge(topAlert.id)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-900/90 border border-slate-700 hover:border-emerald-500/60 hover:text-emerald-300 text-xs font-semibold text-slate-200 transition shadow-sm cursor-pointer"
          >
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span>Gestionar / Marcar Revisada</span>
          </button>

          <button
            onClick={onOpenAlertsCenter}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white transition shadow-lg cursor-pointer ${
              isCritical
                ? 'bg-rose-600 hover:bg-rose-500 shadow-rose-600/30'
                : 'bg-amber-600 hover:bg-amber-500 shadow-amber-600/30'
            }`}
          >
            <span>Ver Centro de Triaje</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
