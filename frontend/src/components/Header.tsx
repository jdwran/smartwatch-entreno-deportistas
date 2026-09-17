import React from 'react';
import { AthleteProfile, ProviderConnection } from '../types';
import { Activity, Watch, ShieldCheck, RefreshCw, Zap } from 'lucide-react';

interface HeaderProps {
  athletes: AthleteProfile[];
  selectedAthlete: AthleteProfile | null;
  onSelectAthlete: (athlete: AthleteProfile) => void;
  connections: ProviderConnection[];
  onOpenDevices: () => void;
  onRefresh: () => void;
  loading: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  athletes,
  selectedAthlete,
  onSelectAthlete,
  connections,
  onOpenDevices,
  onRefresh,
  loading
}) => {
  const connectedCount = connections.filter(c => c.connected).length;

  return (
    <header className="border-b border-slate-800/80 bg-[#0a0d14]/90 backdrop-blur sticky top-0 z-30 px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        
        {/* Brand & Title */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-400 p-0.5 shadow-lg shadow-cyan-500/20">
            <div className="h-full w-full bg-[#090d16] rounded-[10px] flex items-center justify-center">
              <Activity className="h-5 w-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-black tracking-wider text-white">APEX</span>
              <span className="text-xs px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-semibold border border-cyan-500/20">
                PRO TELEMETRY
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Síntesis Fisiológica Multidispositivo para Alto Rendimiento
            </p>
          </div>
        </div>

        {/* Center: Device Connect Status Pill */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenDevices}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-700/80 hover:border-cyan-500/50 transition text-xs text-slate-300 hover:text-white"
          >
            <Watch className="h-3.5 w-3.5 text-cyan-400" />
            <span>Dispositivos:</span>
            <span className="font-semibold text-emerald-400 flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              {connectedCount} Activos
            </span>
          </button>

          {/* Athlete Selector */}
          <div className="flex items-center gap-2 bg-slate-900/90 border border-slate-800 rounded-lg p-1">
            <span className="text-xs text-slate-400 pl-2">Atleta:</span>
            <select
              value={selectedAthlete?.id || ''}
              onChange={(e) => {
                const ath = athletes.find(a => a.id === e.target.value);
                if (ath) onSelectAthlete(ath);
              }}
              className="bg-transparent text-xs font-semibold text-white focus:outline-none pr-2 py-1 cursor-pointer"
            >
              {athletes.map(a => (
                <option key={a.id} value={a.id} className="bg-slate-900 text-white">
                  {a.name} ({a.sport.split('/')[0]})
                </option>
              ))}
            </select>
          </div>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={loading}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-cyan-400 transition disabled:opacity-50"
            title="Sincronizar telemetría"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        </div>

      </div>
    </header>
  );
};
